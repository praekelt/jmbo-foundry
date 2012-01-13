Start up the credential server 
------------------------------
cd login
$PYTHON/bin/fl-credential-ctl credential.conf start

Run a test
----------
$PYTHON/bin/fl-run-test --simple-fetch test_Foundry.py

Run a bench
-----------
$PYTHON/bin/fl-run-bench --simple-fetch test_Foundry.py Foundry.test_foundry

Build a report
--------------
$PYTHON/bin/fl-build-report foundry-bench.xml  | view -
