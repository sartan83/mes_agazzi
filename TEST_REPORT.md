# Test report — Java 17 migration

- Generated: 2026-09-28 12:12 UTC
- Commit: `a627be1151` (branch `java17-migration`)
- JDK: `openjdk version "17.0.19" 2026-04-21`
- Maven: `Apache Maven 3.9.9 (8e8579a9e76f7d015ee5ec7bfcdc97d260186937)`
- Command: `mvn -B -Ptomcat clean install && mvn -B org.apache.maven.plugins:maven-surefire-report-plugin:3.5.3:report-only -Daggregate=true`
- HTML: [`TEST_REPORT.html`](TEST_REPORT.html) (this summary with per-module drill-down), Surefire aggregate: [`docs/test-report/surefire-report.html`](docs/test-report/surefire-report.html)

## Totals

| Tests | Passed | Failed | Errors | Skipped | Test classes | Line coverage | Branch coverage |
|--:|--:|--:|--:|--:|--:|--:|--:|
| 823 | 793 | 0 | 0 | 30 | 193 | 5.1% (3769/73522) | 4.7% (1170/25085) |

Baseline (unmodified `master`, JDK 1.8.0_504): 822 tests, 0 failures, 0 errors, 29 skipped. The extra test/skip on JDK 17 is `TSFOrderSuppliesOrderStateValidationServiceTest` (no active test methods, `@Ignore`d; see `MIGRATION_NOTES.md`).

## Per module

| Module | Tests | Passed | Failed | Errors | Skipped | Line coverage | Branch coverage | JDK 8 baseline (tests / skipped) |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| `mes-plugins-advanced-genealogy` | 46 | 44 | 0 | 0 | 2 | 17.7% | 18.5% | 46 / 2 |
| `mes-plugins-assignment-to-shift` | 24 | 24 | 0 | 0 | 0 | 13.1% | 7.4% | 24 / 0 |
| `mes-plugins-avg-labor-cost-calc-for-order` | 2 | 2 | 0 | 0 | 0 | 7.6% | 5.3% | 2 / 0 |
| `mes-plugins-basic-production-counting` | 1 | 1 | 0 | 0 | 0 | 0.0% | 0.0% | 1 / 0 |
| `mes-plugins-basic` | 33 | 33 | 0 | 0 | 0 | 3.7% | 3.0% | 33 / 0 |
| `mes-plugins-cat-numbers-in-deliveries` | 17 | 16 | 0 | 0 | 1 | 43.0% | 32.7% | 17 / 1 |
| `mes-plugins-cat-numbers-in-negot` | 11 | 10 | 0 | 0 | 1 | 64.9% | 57.7% | 11 / 1 |
| `mes-plugins-cmms-machine-parts` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-column-extension` | 4 | 4 | 0 | 0 | 0 | 31.9% | 26.9% | 4 / 0 |
| `mes-plugins-cost-calculation` | 2 | 2 | 0 | 0 | 0 | 1.0% | 2.3% | 2 / 0 |
| `mes-plugins-cost-norms-for-materials` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-cost-norms-for-operation-in-order` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-cost-norms-for-operation` | 3 | 3 | 0 | 0 | 0 | 55.3% | 32.1% | 3 / 0 |
| `mes-plugins-cost-norms-for-product` | 5 | 5 | 0 | 0 | 0 | 39.5% | 29.0% | 5 / 0 |
| `mes-plugins-deliveries-min-state` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-deliveries-to-material-flow` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-deliveries` | 57 | 47 | 0 | 0 | 10 | 2.7% | 1.9% | 57 / 10 |
| `mes-plugins-deviation-causes-reporting` | 11 | 11 | 0 | 0 | 0 | 15.5% | 27.8% | 11 / 0 |
| `mes-plugins-email-notifications` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-gantt-for-operation` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-gantt-for-shifts` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-line-changeover-norms-for-orders` | 46 | 45 | 0 | 0 | 1 | 70.9% | 58.1% | 46 / 1 |
| `mes-plugins-line-changeover-norms` | 14 | 14 | 0 | 0 | 0 | 47.9% | 29.8% | 14 / 0 |
| `mes-plugins-master-orders` | 14 | 14 | 0 | 0 | 0 | 1.2% | 1.6% | 14 / 0 |
| `mes-plugins-material-flow-resources` | 6 | 6 | 0 | 0 | 0 | 0.6% | 0.3% | 6 / 0 |
| `mes-plugins-material-flow` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-material-requirement-coverage-for-order` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-material-requirements` | 9 | 9 | 0 | 0 | 0 | 4.2% | 1.0% | 9 / 0 |
| `mes-plugins-operation-cost-calculations` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-operation-time-calculations` | 24 | 24 | 0 | 0 | 0 | 23.2% | 14.6% | 24 / 0 |
| `mes-plugins-order-supplies` | 23 | 23 | 0 | 0 | 0 | 2.0% | 1.0% | 23 / 0 |
| `mes-plugins-orders-for-subproducts-generation` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-orders` | 111 | 111 | 0 | 0 | 0 | 5.5% | 4.8% | 111 / 0 |
| `mes-plugins-product-catalog-numbers` | 6 | 6 | 0 | 0 | 0 | 76.3% | 60.0% | 6 / 0 |
| `mes-plugins-product-flow-thru-division` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-production-counting` | 18 | 18 | 0 | 0 | 0 | 1.3% | 1.5% | 18 / 0 |
| `mes-plugins-production-lines` | 0 | 0 | 0 | 0 | 0 | 0.0% | 0.0% | 0 / 0 |
| `mes-plugins-production-per-shift` | 35 | 35 | 0 | 0 | 0 | 7.0% | 9.6% | 35 / 0 |
| `mes-plugins-production-scheduling` | 4 | 4 | 0 | 0 | 0 | 2.4% | 4.6% | 4 / 0 |
| `mes-plugins-states` | 70 | 70 | 0 | 0 | 0 | 33.4% | 37.9% | 70 / 0 |
| `mes-plugins-stoppage` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-supply-negotiations` | 43 | 43 | 0 | 0 | 0 | 4.6% | 2.6% | 43 / 0 |
| `mes-plugins-tech-subcontr-for-deliveries` | 13 | 13 | 0 | 0 | 0 | 20.0% | 3.3% | 13 / 0 |
| `mes-plugins-tech-subcontr-for-negot` | 13 | 13 | 0 | 0 | 0 | 16.3% | 2.3% | 13 / 0 |
| `mes-plugins-tech-subcontr-for-oper-tasks` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-tech-subcontr-for-order-supplies` | 5 | 4 | 0 | 0 | 1 | 15.7% | 5.3% | 4 / 0 |
| `mes-plugins-tech-subcontr-for-production-counting` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-tech-subcontracting` | 8 | 7 | 0 | 0 | 1 | 2.3% | 0.9% | 8 / 1 |
| `mes-plugins-technologies-generator` | 20 | 15 | 0 | 0 | 5 | 14.3% | 12.8% | 20 / 5 |
| `mes-plugins-technologies` | 58 | 55 | 0 | 0 | 3 | 4.3% | 4.3% | 58 / 3 |
| `mes-plugins-time-gaps-preview` | 25 | 25 | 0 | 0 | 0 | 30.8% | 34.4% | 25 / 0 |
| `mes-plugins-time-norms-for-operations` | 8 | 5 | 0 | 0 | 3 | 3.6% | 2.2% | 8 / 3 |
| `mes-plugins-wage-groups` | 8 | 8 | 0 | 0 | 0 | 72.9% | 80.0% | 8 / 0 |
| `mes-plugins-warehouse-minimal-state` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |
| `mes-plugins-work-plans` | 26 | 24 | 0 | 0 | 2 | 8.3% | 7.7% | 26 / 2 |
| `mes-application` | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 / 0 |

Modules with 0 tests have no test sources on `master`; they are compiled, woven and packaged as part of the same build. Coverage is JaCoCo line/branch coverage of each module's own classes by its own tests (`n/a` = module without tests); the total coverage is computed over the modules that have tests.
