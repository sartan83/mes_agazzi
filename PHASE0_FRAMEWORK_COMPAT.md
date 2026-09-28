# Phase 0 — Qcadoo framework compatibility with Java 17

**Verdict: GO (conditional)** — the external Qcadoo framework binaries can run on Java 17 *as-is* (no framework
rebuild), provided the MES build overrides the framework's transitive Spring/AspectJ/Quartz versions and the JVM is
started with a fixed set of `--add-opens` flags. A full framework rebuild (vendoring `qcadoo/qcadoo`) is **not**
required for this migration and is recorded below as the fallback / long-term option.

Environment used for the investigation: OpenJDK 17.0.19 (`/usr/lib/jvm/java-17-openjdk-amd64`), Temurin 1.8.0_504
(baseline only), Maven 3.9.9.

## 1. Artifacts inspected

All `com.qcadoo:*` artifacts at `${qcadoo.version}` = `1.5-SNAPSHOT` (latest snapshot on
`nexus.qcadoo.org`, built 2026-09-25) referenced from the root `pom.xml`, `mes-application/pom.xml` and the plugin
POMs (directly or transitively):

| Artifact | Class-file major | Java level | Manifest |
|---|---|---|---|
| qcadoo-plugin | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-view | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-security | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-report | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-commons | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-localization | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-testing | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-model | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-mail | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-tenant | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-custom-translation | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-plugins-menu-management | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-plugins-user-management | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-plugins-dictionary-management | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-plugins-custom-translation-management | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-plugins-export | 52 | Java 8 | Maven 3.5.4, Build-Jdk 1.8.0_362 |
| qcadoo-plugins-plugin-management / unit-conversion-management | 52 | Java 8 | same |
| com.qcadoo:qcadoo-maven-plugin 1.5-SNAPSHOT | 52 | Java 8 | same |
| com.qcadoo.maven:qcadoo-super-pom **0.0.1** (parent) | — | enforces Java 1.8 | only version published |

Bytecode was read from the first `.class` entry of each jar (`od` on bytes 6–7). No Java-17 (major 61) build of any
Qcadoo artifact exists on the Qcadoo Nexus (releases or snapshots), and `qcadoo-super-pom` has no version newer than
`0.0.1`. **"Upgrade the super-pom" and "source newer framework releases from Nexus" are therefore not available.**

## 2. Transitive stack (`mvn dependency:tree`, master, unmodified)

| Library | Version brought in by the framework / super-pom | Java 17 status |
|---|---|---|
| Spring Framework | 3.2.11.RELEASE | **Blocker**: bundled ASM 4 cannot read class-file 61 → `BeanDefinitionStoreException: ASM ClassReader failed to parse class file` during component scan of Java-17-compiled MES classes |
| Spring Security | 3.2.5.RELEASE | OK on 17 (pure Java 6/7 bytecode, no ASM); needs to run against Spring 4.x → use 3.2.10 (officially supports Spring 4) |
| Hibernate | 3.6.9.Final (+ javassist 3.18.1-GA) | Runs on 17 with `--add-opens java.base/java.lang=ALL-UNNAMED` (javassist `ClassLoader.defineClass` reflection) |
| cglib | 2.2 (mes-application) | Same `defineClass` issue → needs `--add-opens`; Spring 4.3 uses its own repackaged cglib 3.2 |
| AspectJ | 1.8.13 (rt/weaver/tools), `org.codehaus.mojo:aspectj-maven-plugin:1.7` | **Blocker**: plugin needs `tools.jar` (`Could not find artifact com.sun:tools:jar:17.0.19`); ajc 1.8 cannot target 17 |
| Quartz | 1.8.5 | Not usable with Spring 4.x `scheduling.quartz` → Quartz 2.x |
| Jackson | 1.9 (`org.codehaus.jackson`) | OK on 17; only the Spring 3.2 view class `MappingJacksonJsonView` (removed in Spring 4.1) is referenced by `qcadoo-view.jar!/qcadoo-web-context.xml` |
| Tiles | 2.2.2 | OK on 17; `view.tiles2` still present in Spring 4.3 |
| Servlet API | `javax.servlet` 3.1 | Stays **javax** (Tomcat 8.5.12 bundled by `qcadoo-maven-plugin`, Spring 4.3). No Jakarta migration. |
| JUnit / Mockito / PowerMock | 4.9 / 1.10.8 / 1.5.6 | Evaluated in Phase 2 (need `--add-opens` for PowerMock) |
| Other: xml-apis 1.4.01, stax-api 1.0.1 | via esapi / xercesImpl / jasperreports / xmlbeans | Break ajc ≥ Java 9 compliance ("package javax.xml.stream is accessible from more than one module") → exclude |

## 3. Runtime probes on Java 17

A stand-alone probe (component scan + cglib + javassist proxy of a class compiled with `--release 8` vs `--release 17`)
was run on JDK 17 against each Spring line:

| Spring | Scan Java 8 class | Scan Java 17 class | cglib/javassist proxy, no flags | … with `--add-opens java.base/java.lang=ALL-UNNAMED` |
|---|---|---|---|---|
| 3.2.11 (current) | OK | **FAIL** (ASM) | FAIL (`InaccessibleObjectException`) | OK |
| 4.3.30.RELEASE | OK | OK | FAIL (legacy cglib 2.2 / javassist 3.18) | OK |
| 5.3.39 | OK | OK | FAIL (legacy cglib 2.2 / javassist 3.18) | OK |

API surface check: `jdeps -verbose:class` of every `qcadoo-*.jar` against Spring **4.3.30** resolved every
`org.springframework.*` class reference (only Spring Security classes were reported, as expected because they live in
separate jars). The Spring classes named in framework XML (`qcadoo-web-context.xml`, `root-context.xml`) were checked
individually: all exist in 4.3.30 (`tiles2.TilesConfigurer`, `DefaultAnnotationHandlerMapping`,
`AnnotationMethodHandlerAdapter`, `orm.hibernate3.*`, `Log4jConfigListener`, …) **except**
`org.springframework.web.servlet.view.json.MappingJacksonJsonView`.

Spring 5.x is *not* viable without rebuilding the framework: it removed `orm.hibernate3`, `view.tiles2`,
`DefaultAnnotationHandlerMapping`/`AnnotationMethodHandlerAdapter`, `Log4jConfigListener`, and Spring Security 3.2 is not
compatible with it.

## 4. Decision

**Option chosen: keep the published Qcadoo 1.5-SNAPSHOT framework binaries (Java 8 bytecode, which the Java 17 JVM loads
fine) and override their stack from the MES root POM:**

| Property / artifact | From | To |
|---|---|---|
| `spring.version` (via `spring-framework-bom` import) | 3.2.11.RELEASE | **4.3.30.RELEASE** (last 4.x, reads Java 17 bytecode) |
| `spring.security.version` (via `spring-security-bom`) | 3.2.5.RELEASE | **3.2.10.RELEASE** |
| `aspectj.version` | 1.8.13 | **1.9.24** |
| AspectJ Maven plugin | `org.codehaus.mojo:aspectj-maven-plugin:1.7` | **`dev.aspectj:aspectj-maven-plugin:1.14.1`** |
| `quartz` | 1.8.5 | **2.3.2** (Spring 4 `CronTriggerFactoryBean`) |
| `maven.compiler.release` | 1.8 | **17** |
| `javax.annotation:javax.annotation-api` | JDK-provided | **1.3.2** explicit (`@PostConstruct` removed from JDK 11+) |
| parent `qcadoo-super-pom` | 0.0.1 | 0.0.1 (no newer version exists; overridden locally) |
| `qcadoo.version` | 1.5-SNAPSHOT | 1.5-SNAPSHOT (no Java 17 build exists) |

Consequences for later phases:

1. **Namespace**: stay on `javax.*` (servlet, annotation, xml). No Jakarta migration.
2. **Quartz**: every `org.springframework.scheduling.quartz.CronTriggerBean` → `CronTriggerFactoryBean`; code typed
   against `CronTriggerBean` → `org.quartz.CronTrigger`.
3. **MappingJacksonJsonView**: provide a compatibility copy of the Spring 3.2 class (Apache-2.0) in `mes-application` so
   that `qcadoo-web-context.xml` keeps working unchanged.
4. **JVM flags**: tests (Surefire `argLine`) and Tomcat (`setenv`) must add the `--add-opens` set defined in the root
   POM property `jdk17.opens`, plus `-javaagent` pointing at `aspectjweaver-1.9.24.jar`.
5. **xml-apis / stax-api** excluded centrally via `dependencyManagement` (JDK provides these packages).

Fallback (no-go path, only if Phase 3 finds a framework-internal runtime incompatibility): vendor
`github.com/qcadoo/qcadoo` at the commit matching 1.5-SNAPSHOT, build it with `--release 17` on the same Spring 4.3 /
Security 3.2.10 stack and publish it to the local repository as `1.5-java17-SNAPSHOT`.

## 5. Validation of the decision (Phase 1, JDK 17.0.19)

The GO decision was validated end to end on the Phase 1 foundation before any module fan-out:

| Check | Result |
|---|---|
| `mvn -Ptomcat -DskipTests clean install` (all 55 plugins + `mes-application`) | **BUILD SUCCESS**, all classes major 61, `target/mes-application.zip` produced |
| Full test suite on JDK 17 | 823 run / 30 skipped (JDK 8 baseline: 822 / 29; the extra skipped entry is the empty `TSFOrderSuppliesOrderStateValidationServiceTest`, see notes); only failures were Mockito 1 → 3 matcher semantics in tests (see `MIGRATION_NOTES.md`), fixed per stream in Phase 2 |
| Boot packaged Tomcat on JDK 17 against PostgreSQL 14 | Spring root context and `Qcadoo MES` DispatcherServlet initialise, Hibernate schema created, Quartz 2 schedulers start, login + `/dashboard.html` render (byte-identical page size to the JDK 8 baseline boot) |

Two further framework-level incompatibilities were found during the boot and are handled without rebuilding the
framework (confirming that the fallback is not needed):

1. `qcadoo-view.jar!/qcadoo-web-context.xml` configures `ContentNegotiatingViewResolver.mediaTypes`, a setter removed in
   Spring 4. `mes-application/src/main/webapp/WEB-INF/java17-compat-context.xml` (loaded last in `web.xml`) re-declares
   the bean with the same id using the Spring 4 `ContentNegotiationManagerFactoryBean` and the identical media-type map.
2. `qcadoo-maven-plugin`'s bundled `bin/setenv.sh` hard-codes `-javaagent:.../aspectjweaver-1.8.13.jar`. The `tomcat`
   profile of `mes-application/pom.xml` now post-processes `setenv.sh` (weaver version + `jdk17.opens`) and re-zips the
   package.
