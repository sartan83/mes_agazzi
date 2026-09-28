# Note di migrazione Java 17

Branch di migrazione: `java17-migration` (base `master`).

## Avanzamento

Lo stato di avanzamento (fasi, pesi, percentuali per modulo e totale) è tracciato esclusivamente in [`MIGRATION_PROGRESS.md`](MIGRATION_PROGRESS.md), che è il punto unico di verità: non riportare percentuali in questo file.

## Fasi

- **Fase 0** — verifica compatibilità del framework Qcadoo esterno (`com.qcadoo:*`) e del parent `qcadoo-super-pom:0.0.1`.
- **Fase 1** — fondamenta build: sostituzione di `org.codehaus.mojo:aspectj-maven-plugin`, `source`/`target`/`complianceLevel` a 17 nel `pom.xml` root.
- **Fase 2** — migrazione dei moduli `mes-plugins/mes-plugins-*` e `mes-application`.
- **Fase 3** — integrazione e avvio runtime su JDK 17 + PostgreSQL.
- **Fase 4** — test completi, report Surefire/JaCoCo, video.
