# Synthetic fixtures

Public, source-controlled acceptance cases belong here. Mark every invented value as synthetic and include expected results.

`saul_affordability_cases.json` contains invented affordable, unaffordable and missing-commitments cases used by the executable finance tests. It deliberately does not copy the owner's actual balance or butter values.

`bobathan_ingredient_stock_case.json` is a bounded, entirely invented ingredient-stock document. It deliberately demonstrates available flour after reservations, a known egg shortage from zero stock and an explicitly unknown butter quantity. No real stock count is implied.

Saul's reviewed butter case uses deliberately supplied current business facts, so it remains under ignored `data/private/` and is exercised only by the opt-in private integration test.
