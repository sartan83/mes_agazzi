# Avanzamento migrazione Java 17

Punto unico di verità sull'avanzamento della migrazione di `mes_agazzi` a Java 17 (branch `java17-migration`).
Le note tecniche della migrazione sono in [`MIGRATION_NOTES.md`](MIGRATION_NOTES.md).

## Tabella delle fasi

| Fase | Attività | Peso sul totale | Completamento fase (%) | Contributo al totale (%) |
|------|----------|----------------:|-----------------------:|-------------------------:|
| 0 | Verifica compatibilità Java 17 del framework Qcadoo esterno (`com.qcadoo:*`, versione `${project.version}` = `1.5-SNAPSHOT`) e del parent `com.qcadoo.maven:qcadoo-super-pom:0.0.1` | 10% | 100% | 10.00% |
| 1 | Fondamenta build: sostituzione di `org.codehaus.mojo:aspectj-maven-plugin` con toolchain compatibile Java 17; `source`/`target`/`complianceLevel` a 17 nel `pom.xml` root | 5% | 100% | 5.00% |
| 2 | Migrazione dei moduli (vedi [dettaglio Fase 2](#dettaglio-fase-2--migrazione-dei-moduli)) — 0/56 moduli `FATTO` | 65% | 0.00% | 0.00% |
| 3 | Integrazione + avvio runtime su JDK 17 + PostgreSQL | 12% | 0% | 0.00% |
| 4 | Test completi, report Surefire/JaCoCo, video (vedi [stato parziale Fase 4](#stato-parziale-fase-4)) | 8% | 0% | 0.00% |
| **Totale** | | **100%** | | **15.00%** |

## Dettaglio Fase 2 — migrazione dei moduli

Moduli enumerati dalla sezione `<modules>` di `mes-plugins/pom.xml` (55 moduli `mes-plugins-*`, tutti presenti come directory sotto `mes-plugins/`, nell'ordine del reactor) più `mes-application` (dal `pom.xml` root): **56 moduli totali**.
La colonna "File di test" è il numero di file `*Test*.java` sotto `src/test` al commit base (informativa: un modulo senza test è `FATTO` quando compila su Java 17 e `mvn -pl <module> -am test` termina con `BUILD SUCCESS`).

Stati ammessi: `TODO` / `IN CORSO` / `FATTO (test verdi)`.

| # | Modulo | File di test | Stato |
|--:|--------|-------------:|-------|
| 1 | `mes-plugins/mes-plugins-orders` | 16 | FATTO (test verdi) |
| 2 | `mes-plugins/mes-plugins-basic` | 13 | TODO |
| 3 | `mes-plugins/mes-plugins-material-requirements` | 5 | TODO |
| 4 | `mes-plugins/mes-plugins-work-plans` | 7 | TODO |
| 5 | `mes-plugins/mes-plugins-technologies` | 13 | FATTO (test verdi) |
| 6 | `mes-plugins/mes-plugins-production-scheduling` | 1 | FATTO (test verdi) |
| 7 | `mes-plugins/mes-plugins-stoppage` | 0 | TODO |
| 8 | `mes-plugins/mes-plugins-gantt-for-operation` | 0 | FATTO (test verdi) |
| 9 | `mes-plugins/mes-plugins-gantt-for-shifts` | 0 | FATTO (test verdi) |
| 10 | `mes-plugins/mes-plugins-material-flow` | 0 | TODO |
| 11 | `mes-plugins/mes-plugins-material-flow-resources` | 2 | TODO |
| 12 | `mes-plugins/mes-plugins-time-norms-for-operations` | 4 | FATTO (test verdi) |
| 13 | `mes-plugins/mes-plugins-cost-norms-for-operation` | 1 | TODO |
| 14 | `mes-plugins/mes-plugins-cost-norms-for-product` | 1 | TODO |
| 15 | `mes-plugins/mes-plugins-cost-calculation` | 1 | TODO |
| 16 | `mes-plugins/mes-plugins-production-counting` | 4 | TODO |
| 17 | `mes-plugins/mes-plugins-basic-production-counting` | 2 | TODO |
| 18 | `mes-plugins/mes-plugins-cost-norms-for-materials` | 0 | TODO |
| 19 | `mes-plugins/mes-plugins-production-lines` | 1 | TODO |
| 20 | `mes-plugins/mes-plugins-operation-time-calculations` | 1 | FATTO (test verdi) |
| 21 | `mes-plugins/mes-plugins-operation-cost-calculations` | 0 | TODO |
| 22 | `mes-plugins/mes-plugins-deviation-causes-reporting` | 2 | TODO |
| 23 | `mes-plugins/mes-plugins-production-per-shift` | 13 | FATTO (test verdi) |
| 24 | `mes-plugins/mes-plugins-line-changeover-norms` | 5 | TODO |
| 25 | `mes-plugins/mes-plugins-line-changeover-norms-for-orders` | 6 | TODO |
| 26 | `mes-plugins/mes-plugins-states` | 13 | TODO |
| 27 | `mes-plugins/mes-plugins-wage-groups` | 3 | TODO |
| 28 | `mes-plugins/mes-plugins-assignment-to-shift` | 6 | TODO |
| 29 | `mes-plugins/mes-plugins-cost-norms-for-operation-in-order` | 0 | TODO |
| 30 | `mes-plugins/mes-plugins-avg-labor-cost-calc-for-order` | 1 | TODO |
| 31 | `mes-plugins/mes-plugins-product-catalog-numbers` | 2 | TODO |
| 32 | `mes-plugins/mes-plugins-tech-subcontracting` | 5 | TODO |
| 33 | `mes-plugins/mes-plugins-tech-subcontr-for-oper-tasks` | 0 | TODO |
| 34 | `mes-plugins/mes-plugins-deliveries` | 16 | TODO |
| 35 | `mes-plugins/mes-plugins-tech-subcontr-for-deliveries` | 8 | TODO |
| 36 | `mes-plugins/mes-plugins-column-extension` | 1 | TODO |
| 37 | `mes-plugins/mes-plugins-deliveries-to-material-flow` | 0 | TODO |
| 38 | `mes-plugins/mes-plugins-tech-subcontr-for-production-counting` | 0 | TODO |
| 39 | `mes-plugins/mes-plugins-cat-numbers-in-deliveries` | 7 | TODO |
| 40 | `mes-plugins/mes-plugins-master-orders` | 3 | TODO |
| 41 | `mes-plugins/mes-plugins-cmms-machine-parts` | 0 | TODO |
| 42 | `mes-plugins/mes-plugins-warehouse-minimal-state` | 0 | TODO |
| 43 | `mes-plugins/mes-plugins-advanced-genealogy` | 9 | TODO |
| 44 | `mes-plugins/mes-plugins-supply-negotiations` | 10 | TODO |
| 45 | `mes-plugins/mes-plugins-cat-numbers-in-negot` | 5 | TODO |
| 46 | `mes-plugins/mes-plugins-product-flow-thru-division` | 0 | TODO |
| 47 | `mes-plugins/mes-plugins-material-requirement-coverage-for-order` | 0 | TODO |
| 48 | `mes-plugins/mes-plugins-tech-subcontr-for-negot` | 8 | TODO |
| 49 | `mes-plugins/mes-plugins-tech-subcontr-for-order-supplies` | 4 | TODO |
| 50 | `mes-plugins/mes-plugins-order-supplies` | 5 | TODO |
| 51 | `mes-plugins/mes-plugins-orders-for-subproducts-generation` | 0 | FATTO (test verdi) |
| 52 | `mes-plugins/mes-plugins-time-gaps-preview` | 3 | FATTO (test verdi) |
| 53 | `mes-plugins/mes-plugins-technologies-generator` | 5 | FATTO (test verdi) |
| 54 | `mes-plugins/mes-plugins-email-notifications` | 0 | TODO |
| 55 | `mes-plugins/mes-plugins-deliveries-min-state` | 0 | TODO |
| 56 | `mes-application` | 0 | TODO |

**Riepilogo Fase 2:** FATTO 0 / 56 — IN CORSO 0 — TODO 56 → completamento Fase 2 = **0.00%**

## Stato parziale Fase 4

La Fase 4 può avanzare per milestone (ciascuna vale 0% o il suo intero peso interno):

| Milestone Fase 4 | Peso interno | Stato |
|------------------|-------------:|-------|
| Test completi eseguiti e verdi (`mvn test` su tutto il reactor, JDK 17) | 50% | TODO |
| Report Surefire + JaCoCo generati e pubblicati | 30% | TODO |
| Video dimostrativo prodotto | 20% | TODO |

Completamento Fase 4 = somma dei pesi interni delle milestone `FATTO`.

## Regole di aggiornamento

1. **Moduli (Fase 2).** Ogni agente che completa un modulo — compilazione Java 17 OK **e** test JUnit del modulo verdi tramite `mvn -pl <module> -am test` — aggiorna nello stesso commit:
   - la riga del modulo a `FATTO (test verdi)` (usare `IN CORSO` quando si inizia a lavorarci, per evitare lavoro duplicato);
   - il riepilogo Fase 2 e la riga Fase 2 della tabella delle fasi;
   - la riga **Totale**;
   - la sezione [Ultimo aggiornamento](#ultimo-aggiornamento).
2. **Formula Fase 2.** Completamento Fase 2 (%) = `moduli FATTO / 56 × 100`. Ogni modulo vale quindi 100/56 ≈ 1.79% della fase e 65/56 ≈ 1.16% del totale. Conteggio oggettivo dei moduli completati:
   ```bash
   grep -c '| FATTO (test verdi) |' MIGRATION_PROGRESS.md
   ```
3. **Fasi 0, 1, 3 (non parallelizzabili).** Il completamento passa da 0% a 100% solo quando la fase è interamente conclusa; nessun valore intermedio.
4. **Fase 4.** Si applica la stessa regola 0% → 100%, oppure lo stato parziale per milestone descritto sopra se serve granularità.
5. **Contributo al totale** di ogni fase = `peso × completamento fase / 100`. **Totale** = somma dei contributi. Valori percentuali con 2 decimali (arrotondamento standard).
6. **Ultimo aggiornamento.** A ogni modifica aggiornare data (UTC, `YYYY-MM-DD`) e commit di riferimento (lo SHA del commit su cui è stata verificata la compilazione/i test, abbreviato) più una breve descrizione.

## Ultimo aggiornamento

- **Data:** 2026-09-28
- **Commit di riferimento:** `c0ca06e` (fondamenta build Java 17, introduce `PHASE0_FRAMEWORK_COMPAT.md`)
- **Descrizione:** Fase 0 conclusa (verdetto GO condizionale, vedi `PHASE0_FRAMEWORK_COMPAT.md`); Fase 1 conclusa: `dev.aspectj:aspectj-maven-plugin` 1.14.1, AspectJ 1.9.24, `maven.compiler.release=17`, stack Spring 4.3.30 / Security 3.2.10 / Quartz 2.3.2; `mvn -Ptomcat -DskipTests clean install` → BUILD SUCCESS su OpenJDK 17.0.19.
