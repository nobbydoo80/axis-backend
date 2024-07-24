#AEC REMRate *(aec_remrate)*
----------------------------

## Description
This app simply houses the data directly as it comes from AEC RemRate.

## Authors

* Steven Klass


## Copyright

Copyright 2011-2023 Pivotal Energy Solutions.  All rights reserved.

### How to update fields in REM/Rate

#### Database Updates

1. Add the fields as needed to each of the models to the app `aec_remrate`

    a. Pay attention new fields need to support null as old versions will not push anything.

2. Using the provided MSSQL Translate that to MySQL equivalent.  An example is similar to this.

```sql
ALTER TABLE `BldgInfo` ADD `nBITotalStories` INT DEFAULT NULL;
UPDATE `Version` SET `lMinor` = 20 WHERE `lID` = 1;
```

3. Run the above SQL data on the REM database.
4. Dump the structure back out. Compare to the prior version (validate changes) and update the version insert.
   `mysqldump -h 127.0.0.1 --no-data --column-statistics=0 --databases remrate > baseline.sql
5. Copy the above sql changes into the remrate_data.models and create the migration.
Run the migration.
```bash
./manage.py makemigrations remrate_data
./manage.py migrate remrate_data
```
6. Recreate the triggers.  `./manage.py build_sql_triggers`.  The update the trigger_drop.sql by running
   `cat axis/aec_remrate/sql/triggers.sql| grep DROP` and pasting that back into the trigger_drop.sql

7. Drop all triggers by running the drop triggers.  We want to just get a mysql insert for this
version of Rem

8. Download and install the full version or REM/Rate that you are working with.  Using the prior
ALL_FIELDS_SET_\<VERSION\>.blg update it ensuring that you toggle some of the new fields. Get the
model names more accurate to the actual fields.  Save this as ALL_FIELDS_SET_\<VERSION\>.blg

9. Flush the database..  Yup really.  You may want to save it off first.  Remember stop it before
you copy it.  `./manage.py flush`

10. Wipe existing logs.  Throttle up debugging on MySQL.  Edit logging.cnf and restart it
with these options.  (They may already be there)
```editorconfig
general_log =1
general_log_file =/var/log/mysql/mysql.log
```

11. Export the file to your local MySQL Server.  Copy the log file to
axis/aec_remrate/data/ALL_FIELDS_\<VERSION\>.sql.  You will then modify this such that it can be used
to test out the triggers side of things.  See the prior versions.  Some helpful regexs are
as follows:

```regexp
\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z\t    \d \w+\s
```

12. Test your SQL File to make sure it works.

13. Add the triggers by running the triggers.sql file

14. Verify the new data makes it over rerun you sql file.

####BLG Parser Updates


####XML BLG Writer Updates


####XML Simulation Writer Updates
