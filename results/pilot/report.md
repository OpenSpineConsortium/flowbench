# flowbench report: pilot

Arms: symphony, script, solo; primary symphony; logs logs.

## Resolved

| arm | n | resolved | rate | Wilson 95% | bootstrap over repositories | of the sample | orchestration failures | timeouts | turn limits | harness errors left out | excluded |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| symphony | 8 | 8 | 100.0% | 68 to 100 | 100 to 100 | 8/8 (100.0%) | 0 | 0 | 0 | 0 | 0 |
| script | 8 | 8 | 100.0% | 68 to 100 | 100 to 100 | 8/8 (100.0%) | 0 | 0 | 0 | 0 | 0 |
| solo | 8 | 7 | 87.5% | 53 to 98 | 57 to 100 | 7/8 (87.5%) | 0 | 0 | 0 | 0 | 0 |

## Comparisons (instances both arms scored)

| comparison | n | only symphony | only the other | gap in points | exact McNemar p |
| --- | --- | --- | --- | --- | --- |
| symphony vs script | 8 | 0 | 0 | +0.0 | 1.000 |
| symphony vs solo | 8 | 1 | 0 | +12.5 | 1.000 |

## Cost and time per instance

| arm | measured | tokens, median | tokens, mean | tokens per resolved | est. USD, mean | cost source | agents' seconds, median | wall seconds, median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| symphony | 8 | 844,384 | 1,010,067 | 1,010,067 | 0.39 | claude code | 91 | 91 |
| script | 8 | 1,131,776 | 1,340,241 | 1,340,241 | 0.50 | claude code | 128 | 120 |
| solo | 8 | 195,654 | 212,119 | 242,422 | 0.10 | claude code | 22 | 51 |

## Cost, paired (instances both arms measured)

| tokens | n | ratio of the sums | bootstrap over repositories |
| --- | --- | --- | --- |
| symphony / script | 8 | 0.75 | 0.67 to 0.82 |
| symphony / solo | 8 | 4.76 | 4.10 to 5.44 |

## Review (arms that ran one)

| arm | findings raised | confirmed | fixed | resolved, with a confirmed finding | resolved, with none |
| --- | --- | --- | --- | --- | --- |
| symphony | 9 | 0 | 7 | 0/0 | 8/8 |
| script | 13 | 7 | 7 | 6/6 | 2/2 |

## Instances

| instance | symphony | script | solo |
| --- | --- | --- | --- |
| astropy__astropy-12907 | pass | pass | pass |
| django__django-12708 | pass | pass | pass |
| django__django-14752 | pass | pass | pass |
| matplotlib__matplotlib-24149 | pass | pass | pass |
| pylint-dev__pylint-7080 | pass | pass | unresolved |
| pytest-dev__pytest-7490 | pass | pass | pass |
| scikit-learn__scikit-learn-14894 | pass | pass | pass |
| sphinx-doc__sphinx-11445 | pass | pass | pass |
