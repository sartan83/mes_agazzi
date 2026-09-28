# Java 8 → Java 17 migration notes

Running log of every non-trivial decision, blocker and dependency bump of the `java17-migration` branch.
Framework go/no-go analysis: [`PHASE0_FRAMEWORK_COMPAT.md`](PHASE0_FRAMEWORK_COMPAT.md).

Branch: `java17-migration` (base `master`).

## Progress

Progress (phases, weights, per-module status and total percentage) is tracked exclusively in
[`MIGRATION_PROGRESS.md`](MIGRATION_PROGRESS.md), the single source of truth; no percentages are reported here.

## Environment

| Item | Value |
|---|---|
| JDK | OpenJDK 17.0.19 (`.tool-versions` pins a JDK 17 for asdf/mise) |
| Maven | 3.9.9 |
| Baseline for comparison | Temurin 1.8.0_504 on unmodified `master`: 822 tests, 0 failures, 0 errors, 29 skipped (37 modules with tests) |
| Database | PostgreSQL 14, database `mes`, user `postgres` (values from `mes-application/conf/tomcat/db.properties`) |

## Phase 0 — framework compatibility (decision: GO, conditional)

Qcadoo 1.5-SNAPSHOT framework jars are Java 8 bytecode (major 52), no Java 17 build or newer `qcadoo-super-pom` exists.
They run on Java 17 once the transitive stack is overridden from the MES root POM (details in the Phase 0 report).

## Phase 1 — build foundation

### Dependency / plugin bumps (root `pom.xml`)

| Artifact | Before (inherited from `qcadoo-super-pom:0.0.1` / framework) | After | Why |
|---|---|---|---|
| Java level | 1.8 (`aspectj-maven-plugin` source/target/complianceLevel) | 17 (`maven.compiler.release`, ajc `complianceLevel`) | target |
| AspectJ Maven plugin | `org.codehaus.mojo:aspectj-maven-plugin:1.7` | `dev.aspectj:aspectj-maven-plugin:1.14.1` | old plugin needs `tools.jar` |
| `aspectj.version` (rt / weaver / tools) | 1.8.13 | 1.9.24 | Java 17 support |
| Spring Framework (`spring-framework-bom` import) | 3.2.11.RELEASE | 4.3.30.RELEASE | Spring 3.2 ASM cannot read class-file 61 |
| Spring Security (`spring-security-bom` import) | 3.2.5.RELEASE | 3.2.10.RELEASE | Spring 4 compatible 3.2.x |
| Quartz | 1.8.5 | 2.3.2 | required by Spring 4 `scheduling.quartz` |
| `javax.annotation:javax.annotation-api` | JDK | 1.3.2 | `javax.annotation` removed from JDK 11+ |
| Mockito | `mockito-all` 1.10.8 | `mockito-core` 3.12.4 | Mockito 1 + PowerMock 1 cannot run on 17 |
| PowerMock | `powermock-api-mockito` 1.5.6 | `powermock-api-mockito2` / `powermock-module-junit4` 2.0.9 | PowerMock 1.x `PowerMockRunner` writes a `final` field via the removed `Field.modifiers` |
| Objenesis | 2.1 | 3.3 | Java 17 instantiation |
| maven-compiler-plugin | super-pom default | 3.13.0 | `release` support |
| maven-surefire-plugin | 2.18 | 3.5.3 | Java 17 forking, `classpathDependencyExcludes` |

### Decisions

1. **Framework stays binary** (Qcadoo 1.5-SNAPSHOT, Java 8 bytecode); `javax.*` namespace is kept everywhere.
2. **Quartz 2**: every `org.springframework.scheduling.quartz.CronTriggerBean` in plugin `root-context.xml` files is now
   `CronTriggerFactoryBean` (only `jobDetail`/`cronExpression` properties are used, both identical in the factory bean);
   `mes-plugins-basic` `TriggersFactoryBean` collects `org.quartz.CronTrigger` instead of `CronTriggerBean`.
3. **xml-apis / stax-api** excluded from `esapi`, `xercesImpl`, `jasperreports`, `xmlbeans` (versions unchanged) —
   the JDK `java.xml` module provides these packages and ajc ≥ 9 rejects split packages
   (`The package javax.xml.stream is accessible from more than one module`).
4. **JVM flags** (`jdk17.opens` property): `--add-opens` for `java.lang`, `java.lang.reflect`, `java.lang.invoke`,
   `java.util`, `java.util.concurrent`, `java.text`, `java.io`, `java.net`, `java.math`, `java.security`,
   `sun.nio.ch`, `java.awt.font`, `java.sql`. Used by Surefire `argLine` and appended to Tomcat `bin/setenv.sh`.
   Needed by cglib 2.2 / javassist 3.18 (`ClassLoader.defineClass`), PowerMock and XStream-style reflection.
5. **Surefire**: the inherited `mockito-all` / `powermock-api-mockito` test jars are removed from the test classpath
   (`classpathDependencyExcludes`); `includes` pinned to the Surefire 2.18 defaults (`Test*`, `*Test`, `*TestCase`) so
   exactly the same test classes run as on `master` (Surefire 3 would additionally pick up `*Tests`).
   `.mvn/test-classpath/org/powermock/extensions/configuration.properties` sets `powermock.global-ignore=jdk.internal.*`.
6. **Spring 4 compatibility for framework XML** (`mes-application`):
   - `org.springframework.web.servlet.view.json.MappingJacksonJsonView` (removed in Spring 4.1, referenced by
     `qcadoo-view.jar!/qcadoo-web-context.xml`) is provided as an unchanged copy of the Spring 3.2 class (Apache-2.0).
   - `WEB-INF/java17-compat-context.xml`, loaded last, re-declares `contentNegotiatingViewResolver` with a
     `ContentNegotiationManagerFactoryBean` holding the identical media-type map (the Spring 3.2 `mediaTypes` setter no
     longer exists).
7. **Tomcat package** (`-Ptomcat`): `qcadoo-maven-plugin` bundles Tomcat 8.5.12 (javax, runs on 17) and a `setenv.sh`
   hard-coding `aspectjweaver-1.8.13.jar`; an antrun step rewrites it to `${aspectj.version}`, appends `jdk17.opens`
   and re-creates `target/mes-application.zip`.
8. **Mockito 1 → 3 test semantics**: Mockito ≥ 2 `any(Foo.class)` / `anyString()` no longer match `null`. Tests whose
   production code passes `null` (e.g. `entity.addError(null, "...")`, `SearchRestrictions` mocked statically → `null`
   criterion) are updated to `Mockito.nullable(Foo.class)`, which is the exact Mockito 1 behaviour. No assertion is
   weakened. These 11 test-file updates are part of the shared base (not of the individual streams) because
   `mvn -pl <module> -am test` also runs the tests of every upstream module (e.g. `mes-plugins-basic`,
   `mes-plugins-orders`, `mes-plugins-states`), so a stream could not be green while another stream still carried
   the fix. Files: `UnitConversionItemValidatorsBTest` (basic), `StateChangeViewClientValidationUtilTest` (states),
   `AssignmentToShiftHooksTest`, `AssignmentToShiftReportHooksTest` (assignment-to-shift), `OrderDetailsHooksTest`
   (orders), `PPSReportHooksTest` (production-per-shift), `CompanyProductHooksTest` (deliveries),
   `NegotiationProductHooksTest` (supply-negotiations), `ProductCatalogNumbersServiceImplTest`
   (product-catalog-numbers), `BatchModelValidatorsTest` (advanced-genealogy).
   `TSFOrderSuppliesOrderStateValidationServiceTest` (tech-subcontr-for-order-supplies) has every `@Test` method
   commented out on `master`; PowerMock 1.5 silently ran 0 tests, PowerMock 2 fails such a class with
   `No runnable methods`, so it is marked `@Ignore` (reported as 1 skipped instead of absent).
9. **Runtime prerequisite (not Java 17 specific)**: `ParameterModelHooks` calls `Currency.getInstance(Locale.getDefault())`,
   so the JVM default locale must contain a country (`LANG=en_US.UTF-8`). Same behaviour on Java 8.

### Blockers found and resolved

| Blocker | Resolution |
|---|---|
| `Could not find artifact com.sun:tools:jar:17.0.19` | `dev.aspectj:aspectj-maven-plugin` |
| `ASM ClassReader failed to parse class file` (Spring 3.2) | Spring 4.3.30 |
| `InaccessibleObjectException ... ClassLoader.defineClass` | `jdk17.opens` |
| ajc split package `javax.xml.stream` | xml-apis / stax-api exclusions |
| PowerMock `IllegalAccessError ... MagicAccessorImpl` / `NoSuchFieldException: modifiers` | PowerMock 2.0.9 + Mockito 3.12.4 |
| `NotWritablePropertyException: mediaTypes` on boot | `java17-compat-context.xml` |
| `-javaagent` pointing at a missing `aspectjweaver-1.8.13.jar` | `setenv.sh` post-processing |

## Phase 2 — module streams

Every module was verified with `mvn -pl <module> -am test` on JDK 17 in its stream branch
(`java17-migration-streams/stream-<x>`, merged via https://github.com/sartan83/mes_agazzi/pull/2 – https://github.com/sartan83/mes_agazzi/pull/6). Git cannot hold both a branch `java17-migration` and branches under `java17-migration/…`, hence the `java17-migration-streams/` prefix. "Test changes" lists the Mockito 3 matcher updates of decision 8.

### Stream A — core / base

Branch `java17-migration-streams/stream-a`.

| Module | `mvn -pl <module> -am test` | Tests | Failures | Errors | Skipped | Main-code changes (Phase 1 base) | Test changes (Phase 1 base) |
|---|---|--:|--:|--:|--:|---|---|
| `mes-plugins-basic` | BUILD SUCCESS | 33 | 0 | 0 | 0 | Quartz 2 `CronTriggerFactoryBean` in `root-context.xml`; `TriggersFactoryBean` → `org.quartz.CronTrigger` | `UnitConversionItemValidatorsBTest` |
| `mes-plugins-states` | BUILD SUCCESS | 70 | 0 | 0 | 0 | none needed | `StateChangeViewClientValidationUtilTest` |
| `mes-plugins-column-extension` | BUILD SUCCESS | 4 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-basic-production-counting` | BUILD SUCCESS | 1 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-production-counting` | BUILD SUCCESS | 18 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-production-lines` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-stoppage` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-deviation-causes-reporting` | BUILD SUCCESS | 11 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-assignment-to-shift` | BUILD SUCCESS | 24 | 0 | 0 | 0 | none needed | `AssignmentToShiftHooksTest`, `AssignmentToShiftReportHooksTest` |
| `mes-plugins-line-changeover-norms` | BUILD SUCCESS | 14 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-line-changeover-norms-for-orders` | BUILD SUCCESS | 46 | 0 | 0 | 1 | none needed | none |
| **Total (module own tests)** | | **221** | **0** | **0** | **1** | | |

No JAXB / JAX-WS, `sun.misc.Unsafe` or other removed JDK API is referenced by these modules (compiled with `--release 17`, no errors); no module-specific blocker.

### Stream B — orders / technologies

Branch `java17-migration-streams/stream-b`.

| Module | `mvn -pl <module> -am test` | Tests | Failures | Errors | Skipped | Main-code changes (Phase 1 base) | Test changes (Phase 1 base) |
|---|---|--:|--:|--:|--:|---|---|
| `mes-plugins-orders` | BUILD SUCCESS | 111 | 0 | 0 | 0 | none needed | `OrderDetailsHooksTest` |
| `mes-plugins-technologies` | BUILD SUCCESS | 58 | 0 | 0 | 3 | Quartz 2 `CronTriggerFactoryBean` in `root-context.xml` | none |
| `mes-plugins-technologies-generator` | BUILD SUCCESS | 20 | 0 | 0 | 5 | none needed | none |
| `mes-plugins-time-norms-for-operations` | BUILD SUCCESS | 8 | 0 | 0 | 3 | none needed | none |
| `mes-plugins-production-scheduling` | BUILD SUCCESS | 4 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-production-per-shift` | BUILD SUCCESS | 35 | 0 | 0 | 0 | Quartz 2 `CronTriggerFactoryBean` in `root-context.xml` | `PPSReportHooksTest` |
| `mes-plugins-operation-time-calculations` | BUILD SUCCESS | 24 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-gantt-for-operation` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-gantt-for-shifts` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-time-gaps-preview` | BUILD SUCCESS | 25 | 0 | 0 | 0 | Quartz 2 `CronTriggerFactoryBean` in `root-context.xml` | none |
| `mes-plugins-orders-for-subproducts-generation` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| **Total (module own tests)** | | **285** | **0** | **0** | **11** | | |

No JAXB / JAX-WS, `sun.misc.Unsafe` or other removed JDK API is referenced by these modules (compiled with `--release 17`, no errors); no module-specific blocker.

### Stream C — deliveries / negotiations

Branch `java17-migration-streams/stream-c`.

| Module | `mvn -pl <module> -am test` | Tests | Failures | Errors | Skipped | Main-code changes (Phase 1 base) | Test changes (Phase 1 base) |
|---|---|--:|--:|--:|--:|---|---|
| `mes-plugins-deliveries` | BUILD SUCCESS | 57 | 0 | 0 | 10 | none needed | `CompanyProductHooksTest` |
| `mes-plugins-deliveries-min-state` | BUILD SUCCESS | 0 | 0 | 0 | 0 | Quartz 2 `CronTriggerFactoryBean` in `root-context.xml` | none |
| `mes-plugins-deliveries-to-material-flow` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-supply-negotiations` | BUILD SUCCESS | 43 | 0 | 0 | 0 | none needed | `NegotiationProductHooksTest` |
| `mes-plugins-cat-numbers-in-deliveries` | BUILD SUCCESS | 17 | 0 | 0 | 1 | none needed | none |
| `mes-plugins-cat-numbers-in-negot` | BUILD SUCCESS | 11 | 0 | 0 | 1 | none needed | none |
| `mes-plugins-order-supplies` | BUILD SUCCESS | 23 | 0 | 0 | 0 | Quartz 2 `CronTriggerFactoryBean` in `root-context.xml` | none |
| `mes-plugins-product-catalog-numbers` | BUILD SUCCESS | 6 | 0 | 0 | 0 | none needed | `ProductCatalogNumbersServiceImplTest` |
| `mes-plugins-material-requirement-coverage-for-order` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-product-flow-thru-division` | BUILD SUCCESS | 0 | 0 | 0 | 0 | Quartz 2 `CronTriggerFactoryBean` in `root-context.xml` | none |
| **Total (module own tests)** | | **157** | **0** | **0** | **12** | | |

No JAXB / JAX-WS, `sun.misc.Unsafe` or other removed JDK API is referenced by these modules (compiled with `--release 17`, no errors); no module-specific blocker.

### Stream D — costs / material flow

Branch `java17-migration-streams/stream-d`.

| Module | `mvn -pl <module> -am test` | Tests | Failures | Errors | Skipped | Main-code changes (Phase 1 base) | Test changes (Phase 1 base) |
|---|---|--:|--:|--:|--:|---|---|
| `mes-plugins-cost-calculation` | BUILD SUCCESS | 2 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-cost-norms-for-operation` | BUILD SUCCESS | 3 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-cost-norms-for-product` | BUILD SUCCESS | 5 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-cost-norms-for-materials` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-cost-norms-for-operation-in-order` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-operation-cost-calculations` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-avg-labor-cost-calc-for-order` | BUILD SUCCESS | 2 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-material-flow` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-material-flow-resources` | BUILD SUCCESS | 6 | 0 | 0 | 0 | Quartz 2 `CronTriggerFactoryBean` in `root-context.xml` | none |
| `mes-plugins-material-requirements` | BUILD SUCCESS | 9 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-warehouse-minimal-state` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| **Total (module own tests)** | | **27** | **0** | **0** | **0** | | |

No JAXB / JAX-WS, `sun.misc.Unsafe` or other removed JDK API is referenced by these modules (compiled with `--release 17`, no errors); no module-specific blocker.

### Stream E — subcontracting / misc / application

Branch `java17-migration-streams/stream-e`.

| Module | `mvn -pl <module> -am test` | Tests | Failures | Errors | Skipped | Main-code changes (Phase 1 base) | Test changes (Phase 1 base) |
|---|---|--:|--:|--:|--:|---|---|
| `mes-plugins-tech-subcontracting` | BUILD SUCCESS | 8 | 0 | 0 | 1 | none needed | none |
| `mes-plugins-tech-subcontr-for-oper-tasks` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-tech-subcontr-for-deliveries` | BUILD SUCCESS | 13 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-tech-subcontr-for-production-counting` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-tech-subcontr-for-negot` | BUILD SUCCESS | 13 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-tech-subcontr-for-order-supplies` | BUILD SUCCESS | 5 | 0 | 0 | 1 | none needed | `TSFOrderSuppliesOrderStateValidationServiceTest` (`@Ignore`, no active test methods) |
| `mes-plugins-advanced-genealogy` | BUILD SUCCESS | 46 | 0 | 0 | 2 | none needed | `BatchModelValidatorsTest` |
| `mes-plugins-cmms-machine-parts` | BUILD SUCCESS | 0 | 0 | 0 | 0 | Quartz 2 `CronTriggerFactoryBean` in `root-context.xml` | none |
| `mes-plugins-work-plans` | BUILD SUCCESS | 26 | 0 | 0 | 2 | none needed | none |
| `mes-plugins-master-orders` | BUILD SUCCESS | 14 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-wage-groups` | BUILD SUCCESS | 8 | 0 | 0 | 0 | none needed | none |
| `mes-plugins-email-notifications` | BUILD SUCCESS | 0 | 0 | 0 | 0 | none needed | none |
| `mes-application` | BUILD SUCCESS | 0 | 0 | 0 | 0 | `MappingJacksonJsonView` shim, `java17-compat-context.xml`, Tomcat `setenv.sh` post-processing | none |
| **Total (module own tests)** | | **133** | **0** | **0** | **6** | | |

No JAXB / JAX-WS, `sun.misc.Unsafe` or other removed JDK API is referenced by these modules (compiled with `--release 17`, no errors); no module-specific blocker.

## Phase 3 — integration

All five stream branches were merged into `java17-migration` (only `MIGRATION_NOTES.md` / `MIGRATION_PROGRESS.md` conflicted:
adjacent table rows, resolved by keeping every stream's rows).

### Full clean build

`mvn -B -Ptomcat clean install` on OpenJDK 17.0.19 / Maven 3.9.9: **BUILD SUCCESS**, 58 reactor projects, 823 tests,
0 failures, 0 errors, 30 skipped. Produces `mes-application/target/mes-application-1.5-SNAPSHOT.war` and the Tomcat
package `mes-application/target/mes-application.zip`.

### Dependency convergence (`mvn dependency:tree`, WAR `WEB-INF/lib` compared with the JDK 8 build of `master`)

| Change | Reason |
|---|---|
| `cglib:cglib` 2.2 → 3.3.0 (`cglib.version`), `org.ow2.asm:asm` managed to 9.7.1 (`asm.version`) | cglib 2.2 depends on `asm:asm:3.1`, which cannot parse class files newer than Java 6; cglib 3.3.0 uses `org.ow2.asm`, pinned to 9.7.1 (reads Java 17 class files). Same `net.sf.cglib` API; `aop.xml` exclusions unchanged. `asm-3.1.jar` is no longer packaged. |
| Spring 3.2.11 → 4.3.30, Spring Security 3.2.5 → 3.2.10, AspectJ 1.8.13 → 1.9.24, Quartz 1.8.5 → 2.3.2, `commons-logging` 1.1.3 → 1.2 | Phase 1 overrides; no Spring 3.2 / AspectJ 1.8 / Quartz 1.x jar remains in the WAR. |
| `xml-apis-1.4.01.jar` removed | Excluded in Phase 1 (split package with `java.xml`). |
| New: `javax.annotation-api-1.3.2`, `c3p0-0.9.5.4` + `mchange-commons-java-0.2.15`, `HikariCP-java7-2.4.13` | `javax.annotation` left the JDK in 11; c3p0 / HikariCP-java7 are Quartz 2.3.2 transitive dependencies (not configured, Quartz keeps its RAM job store). |

Assessment of the other libraries named in the task (all kept, versions unchanged — they run on Java 17 with the
`--add-opens` set above and have no upgrade that keeps the same API):

- `net.sf.ehcache:ehcache-core` 2.3.1 — no JDK-internal API use; cache managers start on JDK 17 (see boot log).
- `org.apache.tiles:*` 2.2.2, `javax.servlet:jstl` 1.2 — plain Servlet/JSP 2.x API, rendered correctly on Tomcat 8.5 / JDK 17 (login, main and dashboard pages).
- `commons-fileupload` 1.2.2 — pure Servlet API, Java 17 compatible; a version bump would be a security change, out of scope.
- `yuicompressor` 2.3.6 — packaged library only, no Java 17 issue.
- Pre-existing duplicates kept as on `master` (same jars in the JDK 8 WAR): `bcprov/bcmail-jdk14` 138 + 1.38 (itext 2.1.7), `saxon` 8.7 + 9.1.0.8, `stax-api-1.0.1` (jettison 1.1; its `javax.xml.stream` classes are shadowed by the JDK `java.xml` module at runtime).

### Boot on PostgreSQL

Fresh boot of the packaged `mes-application.zip` (unzipped, `bin/catalina.sh start`, `JAVA_HOME` = JDK 17,
`LANG=en_US.UTF-8`) against a freshly created PostgreSQL 14 database `mes`:

- `Server startup in 26117 ms`; both Hibernate `SessionFactory`s built (schema created by `hbm2ddl=update`, 488 tables), Quartz `schedulerFactoryBeanBasic` started, `Qcadoo MES` `DispatcherServlet` initialised; no `ERROR`/`SEVERE` entry in `catalina.*.log`, `localhost.*.log` or `root.log`.
- CSRF-protected login (`POST /j_spring_security_check`) → `loginSuccessfull`; `GET /main.html` → 200 (`TEST QCD MES`); `GET /dashboard.html` → 200 (~105 KB dashboard).
- A freshly created database has `afterfirstpswdchange` unset for the default users, so the first login is redirected to the password-change flow (identical on JDK 8 — functional behaviour, not changed). For the automated checks and the demo, `admin` / `superadmin` are marked as having changed the password (`update qcadoosecurity_user set afterfirstpswdchange=true, pswdlastchanged=now()`), i.e. test-data setup only.
- Menu / dashboard fixture: on a freshly created database the `ADMIN` group holds only `ROLE_ADMIN`, while every MES menu item is gated by a functional role (`ROLE_TECHNOLOGIES`, `ROLE_PLANNING`, …), so `admin` sees only the *Administration* menu and an empty dashboard — identical on the JDK 8 build of `master` against a fresh database (verified: same 7 menu entries for `admin`, 9 for `superadmin`). For the demo, the `ADMIN` group was granted all 163 roles (`insert into jointable_group_role(group_id, role_id) select g.id, r.id from qcadoosecurity_group g cross join qcadoosecurity_role r where g.identifier='ADMIN' on conflict do nothing`), again test-data setup only. With that fixture JDK 8 and JDK 17 render the same 186 menu entries for `admin`; the only difference is the relative position of two entries with equal `succession` inside one category (`timeGaps`), i.e. unordered-collection iteration order, not a functional change.
- Dashboard fixture: on a fresh database the `basic_parameter` row has `showChartOnDashboard` / `whatToShowOnDashboard` unset and all 14 `basic_dashboardbutton` rows inactive, so the dashboard body is empty (same on JDK 8). For the demo they were configured as a user would in *Parameters*: `update basic_parameter set showchartondashboard=true, whattoshowondashboard='01orders'; update basic_dashboardbutton set active=true`. Result identical on JDK 8 and JDK 17 for `admin`: chart container, 13 dashboard buttons, orders kanban.
- The *Analysis* menu category label `[orders.menu.analysis, qcadooView.menu.analysis]` is untranslated because no locale file defines that key — identical on JDK 8 (pre-existing).
- Shutdown logs one `SEVERE … checkThreadLocalMapForLeaks` (Spring Security `SecurityContextImpl` thread local) on both JDK 8 and JDK 17 — pre-existing Tomcat leak-detection report, not a regression.
- Load-time weaving reports `error aspect 'com.qcadoo.mes.states.aop.StatesXpiAspect' woven into 'com.qcadoo.mes.states.StateChangeContext' must be defined to the weaver`. The same message is printed by the unmodified `master` on JDK 8 / AspectJ 1.8.13: the class is already compile-time woven by `aspectj-maven-plugin`, and the LTW agent only notes that it does not know the aspect. Not a regression; left as is.

## Phase 4 — full test run, report and demo

### Reporting setup (root `pom.xml`)

| Plugin | Version | Configuration |
|---|---|---|
| `org.jacoco:jacoco-maven-plugin` | 0.8.12 (first line supporting Java 17+ class files well) | `prepare-agent` + `report` bound to `verify`; Surefire `argLine` is now `@{argLine} ${jdk17.opens}` with an empty `argLine` default, so the agent and the module opens are both passed. |
| `org.apache.maven.plugins:maven-surefire-report-plugin` | 3.5.3 (same line as Surefire) | `<reporting>` section, `aggregate=true`. |

### Full run

```bash
mvn -B -Ptomcat clean install
mvn org.apache.maven.plugins:maven-surefire-report-plugin:3.5.3:report-only -Daggregate=true
python3 docs/generate_test_report.py
```

Result on OpenJDK 17.0.19: **823 tests, 793 passed, 0 failures, 0 errors, 30 skipped** in 193 test classes
(JDK 8 baseline of `master`: 822 / 0 / 0 / 29; the difference is the `@Ignore`d, empty
`TSFOrderSuppliesOrderStateValidationServiceTest`). JaCoCo line coverage 5.1 %, branch coverage 4.7 % over the modules with tests.

- Summary (Markdown): [`TEST_REPORT.md`](TEST_REPORT.md) — totals and per-module tests / passed / failed / errors / skipped / coverage, with the JDK 8 baseline per module.
- Summary (HTML): [`TEST_REPORT.html`](TEST_REPORT.html).
- Surefire aggregate HTML report: [`docs/test-report/surefire-report.html`](docs/test-report/surefire-report.html) (copied from `target/reports/surefire.html`).
- Generator: [`docs/generate_test_report.py`](docs/generate_test_report.py); JDK 8 baseline data: [`docs/test-report/baseline-jdk8.json`](docs/test-report/baseline-jdk8.json).

### Demo video

[`docs/java17-migration-demo.mp4`](docs/java17-migration-demo.mp4) — one continuous, annotated recording (edited to ~70 s) on
commit `7ca8e45`: (1) `java -version` / `mvn -v` → OpenJDK 17.0.19, Maven 3.9.9; (2) `mvn -B -Ptomcat clean install` →
BUILD SUCCESS for all 58 reactor projects, 823 tests / 0 failures / 0 errors / 30 skipped; (3) report regeneration and
`TEST_REPORT.html` + Surefire aggregate report opened in Chrome; (4) unzip of `mes-application.zip`, `setenv.sh` with the
AspectJ 1.9.24 agent and `--add-opens`, Tomcat start on JDK 17 (`Server startup in 23222 ms`), `admin` login, dashboard
(13 buttons, chart area, orders kanban), navigation via a dashboard button and the menu to Technologies, Products and
Production orders. Uses the PostgreSQL fixture described in Phase 3. Stills: [`docs/screenshots/`](docs/screenshots/).
