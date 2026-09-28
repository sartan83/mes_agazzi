<a href="https://qcadoo.com"><img src="https://cloud.githubusercontent.com/assets/513146/25782749/bc50ca98-3350-11e7-8837-64fde0f16d48.png" alt="qcadoo MES" /></a>
![beautiful screenshot](https://cloud.githubusercontent.com/assets/513146/25784436/63e0b7c0-336d-11e7-8124-75f860e6f1f0.png)
# qcadoo MES

qcadoo MES is an Internet application for production management targeted at small and medium companies.It combines the functions of large ERP systems, adapting it to the specific character of Small and Medium Companies.

## Quick start

Choose one of the following options:

1. Download the latest binary stable release from
   [GitHub Releases](https://github.com/qcadoo/mes/releases/latest)
2. Build qcadoo MES from sources
   with [this instruction](https://qcadoo.atlassian.net/wiki/display/QCDMESDOC/Building+MES+from+source+code+-+tutorial)

## Building on Java 17

This branch builds and runs on **JDK 17** only (see `MIGRATION_NOTES.md` and `PHASE0_FRAMEWORK_COMPAT.md`).

- JDK: any OpenJDK 17 build (verified with OpenJDK 17.0.19); Maven 3.9.x (verified with 3.9.9). Both are pinned in
  `.tool-versions` for asdf/mise users.
- Build: `mvn clean install` (add `-Ptomcat` to produce `mes-application/target/mes-application.zip`).
- Run: unzip the package and start `bin/catalina.sh start` with `JAVA_HOME` pointing at JDK 17. The generated
  `bin/setenv.sh` already contains the required `--add-opens` flags and the AspectJ 1.9 weaver agent. The JVM default
  locale must include a country (e.g. `LANG=en_US.UTF-8`), because the default currency is derived from it.

## Community vs Commercial version

qcadoo MES comes in two different versions:
- Community version - the Open Source version from this repo
- Commercial version - the version developed and sold by [Qcadoo Limited](https://qcadoo.com/en/)


Commercial version provides i.e.
- full support
- SaaS deployment
- REST API for integration
- ready integration modules with popular ERP software, Pipedrive, SCADA
- additional features (like i.e. Gantt planning, warehouse material flow, maintenance planning module and others)

## Licensing

The code is available under the [GNU AGPLv3](LICENSE.txt).
