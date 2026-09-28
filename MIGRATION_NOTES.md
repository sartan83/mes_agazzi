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
(`java17-migration/stream-<x>`). "Test changes" lists the Mockito 3 matcher updates of decision 8.

### Stream A — core / base

_pending_

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

_pending_

### Stream D — costs / material flow

_pending_

### Stream E — subcontracting / misc / application

_pending_

## Phase 3 — integration

_pending_

## Phase 4 — full test run, report and demo

_pending_
