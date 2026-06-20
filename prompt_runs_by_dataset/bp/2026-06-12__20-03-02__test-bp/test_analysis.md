# Prompt Evaluation Analysis

## Summary
- count: 30
- syntax_pass_rate: 0.9333
- infrastructure_error_rate: 0.0000
- node_precision: 0.3301
- node_recall: 0.2542
- node_f1: 0.2656
- relation_precision: 0.1174
- relation_recall: 0.0868
- relation_f1: 0.0936
- plantuml_compilation_pass_rate: 0.9333
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- missing_activity: 30
- extra_activity: 30
- missing_or_wrong_relation: 30
- extra_or_wrong_relation: 30
- syntax_error: 2

## Representative Failure Cases
### bp-0023
- dataset: bp
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.3729
- relation_f1: 0.1404
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - 1
  - go to promotion jobs home page
  - 2
  - right-click
  - go to external change management id field
  - enter appropriate value
- extra_nodes:
  - promote a joblog into the lifecycle manager tool
  - select job from home page
  - right-click home page screen and click promote
  - enter appropriate value in external change management id field
  - want to create and validate mappings?
  - security settings required?
  - select security option?
  - select promote security
- missing_relations:
  - log in lifecycle manager tool -> selection method
  - selection method -> 1
  - 1 -> go to promotion jobs home page
  - go to promotion jobs home page -> select the job want to promote
  - select the job want to promote -> 2
  - 2 -> right-click
  - right-click -> click promote
  - click promote -> open source and destination systems drop-down lists
- input_excerpt:
  23.	promote a jobLog into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, select the job that you want to promote. You can also right-click the home page screen, and click Promote.3. From the source and the destination systems drop-down lists, select the source and destination systems.Note:Ensure that you have logged into both the source and destination systems before you proceed with the promotion process.4. In the External Change Management ID field, enter the appropriate value, and click Save.5. Click Mappings. Click Edit Mappings if you want to create and validate mappings.6. Click Security Settings, if required. The following options are displayed:• Do not Promote Secur
- generated_excerpt:
  @startuml |User| start :Promote a jobLog into the LifeCycle Manager tool; :Select the job to promote; fork     :Select job from home page; fork again     :Right-click home page screen and click Promote; end fork :Select source and destination systems from drop-down lists; |System| if (Logged into both source and destination systems?) then (No)     |User|     :Log into source and destination systems;     |System| endif |User| :Enter appropriate value in External Change Management ID field; :Click Save; :Click Mappings; if (Want to create and validate mappings?) then (Yes)     :Click Edit Mappings;     :Create and validate mappings; endif :Click Security Settings; if (Security Settings require
### bp-0011
- dataset: bp
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4211
- relation_f1: 0.0000
- missing_nodes:
  - open web application
  - system creates mhtml le
  - all components in one le
  - generate one document and broadcast it?
  - output format is suitable
  - enter recipient email addresses
- extra_nodes:
  - enter the e-mail addresses of the recipients separated with semicolons
  - enter a subject line and text
  - define the importance of the e-mail
  - choose execute
  - create an mhtml file
- missing_relations:
  - open web application -> click on send
  - click on send -> broadcasting wizard appears
  - broadcasting wizard appears -> select output format mhtml
  - select output format mhtml -> system creates mhtml le
  - system creates mhtml le -> all components in one le
  - all components in one le -> generate one document and broadcast it?
  - generate one document and broadcast it? -> output format is suitable
  - output format is suitable -> choose continue
- input_excerpt:
  11.	Broadcasting Web Applications by E-Mail1. In the Web application, click on Send. The Broadcasting Wizard appears; it guides you step-by-step through the required settings.2. Select output format MHTML. The system creates an MHTML le. All components (HTML, style sheet, pictures, and so on) of the entire HTML page are in one le. This output format is suitable if you want to generate one single document and broadcast it by e-mail or to the portal.3. Choose Continue.4. Enter the e-mail addresses of the recipients, separated with semicolons.5. Enter a subject line and text, and dene the importance of the e-mail6. Choose Execute.
- generated_excerpt:
  @startuml partition "User" {     :Click on Send;     :Select output format MHTML;     :Choose Continue;     :Enter the e-mail addresses of the recipients, separated with semicolons;     :Enter a subject line and text;     :Define the importance of the e-mail;     :Choose Execute; }  partition "System" {     :The Broadcasting Wizard appears;     :Create an MHTML file;     note right         All components (HTML, style sheet,         pictures, and so on) of the entire         HTML page are in one file.     end note; } @enduml
### bp-0017
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - go to administration options window
  - click vms settings
  - open version management systems drop-down list
  - select clearcase
  - enter details
  - clearcase map drive
  - enter mvfs s folder name
  - vob tag name
- missing_relations:
  - go to administration options window -> click vms settings
  - click vms settings -> open version management systems drop-down list
  - open version management systems drop-down list -> select clearcase
  - select clearcase -> enter details
  - enter details -> clearcase map drive
  - clearcase map drive -> enter mvfs s folder name
  - enter mvfs s folder name -> vob tag name
  - vob tag name -> enter vob name
- input_excerpt:
  17.	set the ClearCase version management system in Unix1. In the Administration Options window, click VMS Settings.2. From the Version Management Systems drop-down list, select ClearCase.3. Enter the following details:• ClearCase Map Drive - Enter the name of the folder where the MVFSis located. By default, it is /view• VOB Tag Name - Enter the VOB name and the folder where the VOBis located. For example: VobFolder/VobName• View Storage Directory: Enter the path of the directory where the viewsare created.
- generated_excerpt:
  @startuml partition Unix1 {     :In the Administration Options window,     click VMS Settings;     :From the Version Management Systems     drop-down list, select ClearCase;     :Enter the ClearCase Map Drive     (folder where the MVFS is located,     default /view);     :Enter the VOB Tag Name     (VOB name and folder,     e.g. VobFolder/VobName);     :Enter the View Storage Directory     (path where views are created); } @enduml
### bp-0010
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0606
- relation_f1: 0.0000
- missing_nodes:
  - sort revenue data
  - click arrows in revenue eld?
  - sort increasing or decreasing
  - open context menu
  - open context menu
  - choose sort increasing or sort decreasing
  - internet channel is the greatest
  - analyze differences for months?
- extra_nodes:
  - click on the arrows in the revenue field to sort the revenue data in increasing or decreasing order
  - sort method?
  - choose sort increasing or sort decreasing in the context menu
  - select 08.2007 in the dropdown box calendar year/month
  - select 07.2007 in the dropdown box calendar year/month
  - select 09.2007 in the dropdown box to filter the data back to september
  - choose documents > create new comment in the context menu at the subtotal of the distribution channel internet
  - enter a name and description for the document
- missing_relations:
  - sort revenue data -> click arrows in revenue eld?
  - click arrows in revenue eld? -> sort increasing or decreasing
  - sort increasing or decreasing -> click alternative mouse button
  - click alternative mouse button -> open context menu
  - open context menu -> choose sort increasing or sort decreasing
  - choose sort increasing or sort decreasing -> internet channel is the greatest
  - internet channel is the greatest -> analyze differences for months?
  - analyze differences for months? -> open dropdown box calendar year/month
- input_excerpt:
  10.	Analyzing Data in the Web Application1. Since you are interested in the revenue, you want to sort the revenue data.2. Click on the arrows in the Revenue eld to sort the revenue data in increasing or decreasing order.3. You can also sort the revenue by clicking the alternative mouse button on Revenue and choosing Sort Sort Increasing or Sort Decreasing in the context menu. You see that the greatest revenue is obtained with the distribution channel Internet.4. To see the differences in the revenue data for the months July, August and September, select rst 08.2007 and then 07.2007 in the dropdown box Calendar Year/Month. You see that the revenue data for the distribution channel Internet in
- generated_excerpt:
  @startuml partition User {     :Click on the arrows in the Revenue field to sort the revenue data in increasing or decreasing order;          if (Sort method?) then (Context Menu)         :Click alternative mouse button on Revenue;         :Choose Sort Increasing or Sort Decreasing in the context menu;     else (Arrows)     endif          :Select 08.2007 in the dropdown box Calendar Year/Month;     :Select 07.2007 in the dropdown box Calendar Year/Month;     :Select 09.2007 in the dropdown box to filter the data back to September;          :Choose Documents > Create New Comment in the context menu at the subtotal of the distribution channel Internet;     :Enter a name and description for the
### bp-0006
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0667
- relation_f1: 0.0000
- missing_nodes:
  - go to modeling area
  - choose info provider
  - info area displays information
  - transformation
  - data source
  - attributes
  - texts
  - open data source context menu
- extra_nodes:
  - in the modeling area choose info provider
  - go to the tab page schedule and choose start
  - display the next screen
  - select the date and choose execute
  - display the monitor for the load process
  - perform steps for attributes and then for texts of the characteristic?
- missing_relations:
  - go to data warehousing workbench -> go to modeling area
  - go to modeling area -> choose info provider
  - choose info provider -> info area displays information
  - info area displays information -> transformation
  - transformation -> data source
  - data source -> attributes
  - attributes -> texts
  - texts -> open data source context menu
- input_excerpt:
  6.	Loading Master Data forCharacteristic "Product"Go to the Data Warehousing Workbench;in the Modeling area choose Info Provider. The attributes and texts are displayed with transformation and Data source in your Info Area below the characteristic Product.3. Perform the following steps, rst for the attributes of the characteristic and then for the texts of the characteristic.4. From the context menu of the Data source, choose Create Info Package...5. On the next screen, enter a description for the Info Package and choose Save. The Info Package maintenance screen for the scheduler appears.6. Go to the tab page Schedule and choose Start.7. To check the load process, choose Monitor in the toolb
- generated_excerpt:
  @startuml start  partition User {     :Go to the Data Warehousing Workbench;     :In the Modeling area choose Info Provider; }  partition System {     :Display attributes and texts with transformation     and Data source in your Info Area below     the characteristic Product; }  repeat     partition User {         :From the context menu of the Data source,         choose Create Info Package...;         :On the next screen, enter a description         for the Info Package and choose Save;     }      partition System {         :Display the Info Package maintenance screen         for the scheduler;     }      partition User {         :Go to the tab page Schedule and choose Start;         :Choos
### bp-0030
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0714
- relation_f1: 0.0000
- missing_nodes:
  - log in
  - go to promotion jobs
  - click new job
  - new job window appears
  - enter name
  - enter description
  - enter keywords
  - go to save job field
- extra_nodes:
  - log into the lifecycle manager tool
  - in the promotion jobs home page click new job
  - enter the name description and keywords for the job in the appropriate fields
  - in the save job in field browse and select the folder in which you want to save the job
  - select the source system and the destination system from the drop-down lists
  - is the name of the system displayed in the drop-down list?
  - click the login to a new cms option
  - enter the name of the system along with the user name and password in the new window
- missing_relations:
  - log in -> go to promotion jobs
  - go to promotion jobs -> click new job
  - click new job -> new job window appears
  - new job window appears -> enter name
  - enter name -> enter description
  - enter description -> enter keywords
  - enter keywords -> go to save job field
  - go to save job field -> browse and select the folder
- input_excerpt:
  30.	Creating a New Job1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriate fields.4. In the Save Job in field, browse and select the folder in which you want to save the job.5. Select the source system and the destination system from the drop-down lists. If the name of the system is not displayed in the drop-down list, click the Login to a new CMS option. A new window is launched. Enter the name of the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start partition User {     :Log into the LifeCycle Manager tool;     :In the "Promotion Jobs" home page, click New Job;     :Enter the name, description, and keywords for the job in the appropriate fields;     :In the Save Job in field, browse and select the folder in which you want to save the job;     :Select the source system and the destination system from the drop-down lists;     if (Is the name of the system displayed in the drop-down list?) then (No)         :Click the Login to a new CMS option;         :Enter the name of the system along with the user name and password in the new window;     else (Yes)     endif     :Click Create; } @enduml
### bp-0004
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0909
- relation_f1: 0.0000
- missing_nodes:
  - open the toolbar on the right
  - choose choose source system
  - choose the menu option file
  - select source system with technical name pc_file
  - the hierarchical tree is displayed
  - open context menu
  - select create application component...
  - enter technical name and description
- extra_nodes:
  - navigate to modeling functional area of the data warehousing workbench
  - from the toolbar in the right screen area choose choose source system
  - in the menu option file select the source system with technical name pc_file
  - display hierarchical tree of data sources for the source system structured semantically by application component
  - select create application component... from the context menu at the root node of the data source tree
  - enter a technical name and a description for the application component
  - group data sources for this scenario under the application component
  - in the context menu of your application component choose create data source
- missing_relations:
  - choose data sources -> open the toolbar on the right
  - open the toolbar on the right -> choose choose source system
  - choose choose source system -> choose the menu option file
  - choose the menu option file -> select source system with technical name pc_file
  - select source system with technical name pc_file -> the hierarchical tree is displayed
  - the hierarchical tree is displayed -> open context menu
  - open context menu -> select create application component...
  - select create application component... -> enter technical name and description
- input_excerpt:
  4.	Creating Transformations0 Creating Transformations for Master Data of Characteristic "Product"1. You are in the Modeling functional area of the Data Warehousing Workbench.2. Choose Data sources.3. From the toolbar in the right screen area, choose Choose Source System.4. In the menu option File, select the source system with the technical name PC_FILE. A hierarchical tree of the Data sources for this source system is displayed. The Data sources are structured semantically by application component. 5. Select Create application component... from the context menu at the root node of the Data source tree.6. On the next screen, enter a technical name and a description for the application compon
- generated_excerpt:
  @startuml start partition "User" {   :Navigate to Modeling functional area\nof the Data Warehousing Workbench;   :Choose Data sources;   :From the toolbar in the right screen area,\nchoose Choose Source System;   :In the menu option File,\nselect the source system with technical name PC_FILE; } partition "System" {   :Display hierarchical tree of Data sources\nfor the source system,\nstructured semantically by application component; } partition "User" {   :Select Create application component...\nfrom the context menu at the root node\nof the Data source tree;   :Enter a technical name and a description\nfor the application component; } partition "System" {   :Group Data sources for this scen
### bp-0028
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0952
- relation_f1: 0.0000
- missing_nodes:
  - log in
  - more information?
  - see creating a new job
- extra_nodes:
  - log into the lifecycle manager tool
  - select output to a biar file in the destination system drop-down list
  - click create
  - click add objects to add infoobjects to the job
  - use the manage dependencies option to manage the dependencies
  - click promote
  - click export
  - click export
- missing_relations:
  - log in -> create a new job
  - create a new job -> more information?
  - more information? -> see creating a new job
- input_excerpt:
  28.	Exporting a Job to a BIAR File1. Log into the LifeCycle Manager tool, and create a new job. For more information on creating a new job, see Creating a New Job on page 372. In the Destination System drop-down list, select Output to a BIAR file option and click Create.3. Click Add objects to add infoobjects to the job. You can use the Manage Dependencies option to manage the dependencies of the selected job.4. Click Promote.The "Promote - Job Name" screen appears.5. Click Export.The BIAR file is created. You can save a BIAR file to a File System or an FTP location.6. In the "Promote - Job Name"screen, click Biar File Destination. Biar File Destination pane appears.7. Select either File Sys
- generated_excerpt:
  @startuml start partition "LifeCycle Manager" {   :Log into the LifeCycle Manager tool;   :Create a new job;   :Select "Output to a BIAR file" in the Destination System drop-down list;   :Click Create;   :Click Add objects to add infoobjects to the job;   :Use the Manage Dependencies option to manage the dependencies;   :Click Promote;   :Click Export;   :Click Biar File Destination;   if (Select Biar File Destination?) then (File System)     :Select File System;     :Click Export;     :Export the BIAR file to a file system;   else (FTP)     :Select FTP;     :Enter appropriate details in the host, port, username, password, directory, and filename fields;     :Click Export;     :Export the BI

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
