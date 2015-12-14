# IMT5251 Advanced Project Work

Repository for prototype development in the course IMT5251 Advanced Project Work @ GUC/HiG. <br />
The goal of the project is to develop a simple chatbot implementation for use in Open Edx.  <br />
The project is based on the XBlock-SDK (https://github.com/edx/xblock-sdk) environment. <br />
API calls between the prototype and StackExchange is achieved by using Py-StackExchange (https://github.com/lucjon/Py-StackExchange).

# How to install
1. The easiest is to install XBlock-SDK: https://github.com/edx/xblock-sdk
2. After installing XBlock-SDK, you also need to add MySQLDB for Python and Py-StackExchange
  * pip install py-stackexchange
  * pip install python-mysqldb
3. Download this repository and install it to XBlock-SDK by running the following commands: 
  * pip install -e IMT5251_AdvProjWork
  * python xblock-sdk/manage.py syncdb
  * python xblock-sdk/manage.py runserver
