
- For all frameworks needed, please check requirements.txt

How to deploy to production server
- Different server has different steps, here are the general instruction that should apply for all 
1. pull the system from git repository 
2. Install mysql (Tested in mysql  Ver 8.0.18, but above should be fine)
   a. Need to create super user so during server initialization, server will access database to create needed tables
   b. database settings can be found in settings.py
3. Make sure you have java 1.8, python 3, pip installed, because we will use pip to install all other frameworks
4. pip install needed sdks: pip install -r requirements.txt
   a. This command will install django rest framework, mysql connector, and other options
   b. mysqlclient should match version 1.4.6, new version may not work well with python 3
4. Do python manage.py migrate to initialize database 
5. If you use apache server, you may need to manually start the server, in my case, I use pythonanywhere server, which I don't need to
6. After installation, go to admin and add one row entry in settingData table, which is needed for data entry by other tables
7. If you need to store emoji symbols, for gamecore_player.nick_name or other columns, you need to make sure their charsets are set to utf8mb4. By default, settings.py option will only adjust database charset, not mysql innodb
eg.
ALTER TABLE `gamecore_player` CHANGE COLUMN `nick_name` `nick_name` VARCHAR(200) CHARACTER SET 'utf8mb4' NULL DEFAULT NULL;

How to migrate DB tables
1. 
To add/update/ db models:
python manage.py makemigrations
This will create migration file

2. 
To apply the migration
python manage.py migrate

3. 
To import data from xlsx
python manage.py import_gamedata
This will update the db tables with new value. Note this will not erease old data
Make sure 
gamedata/management/commands/resources.py裡已指定了要用的Resource模型，而該模型已在gamedata/admin.py裡寫好並指向新變動的model。

How to add locale 
1. Create the locale file zh_Hant is the language code you want to have translation
python manage.py makemessages -l zh_Hant
2. Compile the locale file, this will create/update the corresponding .mo file
python manage.py compilemessages

How to collect all static files into your static folder
1. Make sure STATIC_ROOT in settings.py is uncommented, which is the destination for all of your static files
python manage.py collectstatic

For Azure App Service + MySQL (Jan2020)
- Setup one app service and one MySQL resources
- Make sure requirement.txt has all the requirement frameworks. This file is needed for azure deployment using visual studio code
- Use Visual Studio Code with Azure tool extension to create app service and do deployment
- Use Azure web portal to create mysql resource 

For Azure VM
- Deploy using git pull from ssh 
- Start service using gunicorn: 
-- To list all gunicorn services
ps ax|grep gunicorn
-- To kill old service 
pkill gunicorn
-- To start new one listening to all incoming request at port 8000
gunicorn --bind 0.0.0.0:8000 happycity.wsgi
-- Or on ubuntu you can use gunicorn3
gunicorn3 --bind 0.0.0.0:8000 happycity.wsgi

emoji information:
https://www.chenshaowen.com/blog/using-utf8mb4-in-django-to-support-emoji-expression.html