# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 0.8500
- infrastructure_error_rate: 0.0000
- node_precision: 0.4533
- node_recall: 0.4251
- node_f1: 0.4307
- relation_precision: 0.3287
- relation_recall: 0.3358
- relation_f1: 0.3311
- plantuml_compilation_pass_rate: 0.8500
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- missing_activity: 16
- extra_activity: 16
- missing_or_wrong_relation: 15
- extra_or_wrong_relation: 15
- syntax_error: 3

## Representative Failure Cases
### bp-0014
- dataset: bp
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.2353
- relation_f1: 0.0000
- missing_nodes:
  - select start
  - select programs
  - select businessobjects xi 3.1
  - select businessobjects enterprise
  - select businessobjects lifecycle manager
  - lifecycle manager login screen appears
  - go to system field
  - enter cms name
- extra_nodes:
  - select start > programs > businessobjects xi 3.1 > businessobjects enterprise > businessobjects lifecycle manager
  - enter the name of the central management server (cms) in the system field
  - select enterprise authentication from the authentication drop-down list
  - ldap authentication
  - select ldap authentication from the authentication drop-down list
  - select windows ad authentication from the authentication drop-down list
- missing_relations:
  - select start -> select programs
  - select programs -> select businessobjects xi 3.1
  - select businessobjects xi 3.1 -> select businessobjects enterprise
  - select businessobjects enterprise -> select businessobjects lifecycle manager
  - select businessobjects lifecycle manager -> lifecycle manager login screen appears
  - lifecycle manager login screen appears -> go to system field
  - go to system field -> enter cms name
  - enter cms name -> enter username and password
- input_excerpt:
  14.	log into the LifeCycle Manager tool.To log into the LifeCycle Manager tool, complete the following steps:1. Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager. The LifeCycle Manager login screen appears.2. In the System field, enter the name of the Central Management Server (CMS) on which the LifeCycle Manager tool is installed.3. Enter the user name and password.4. Select the appropriate authentication method from the Authentication drop-down list.The LifeCycle Manager tool supports the following authentication types:• Enterprise authentication - This authentication type requires a user name and a password that are recognize
- generated_excerpt:
  @startuml start :Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager; :Enter the name of the Central Management Server (CMS) in the System field; :Enter the user name and password; switch case (Enterprise authentication)     :Select Enterprise authentication from the Authentication drop-down list; case (LDAP authentication)     :Select LDAP authentication from the Authentication drop-down list; case (Windows AD)     :Select Windows AD authentication from the Authentication drop-down list; endswitch :Click Log on; @enduml
### rac-0012
- dataset: rac
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4800
- relation_f1: 0.4583
- missing_nodes:
  - switch to state 153
  - condition judgement
  - switch to state 175
  - switch to state 175
  - switch to state 175
  - fast charging is inactive
  - high-voltage shutdown request charging/discharging =2
  - high-voltage shutdown request charging/discharging =2
- extra_nodes:
  - system starts up
  - transition to state 153
  - move to state 175
  - high-voltage shutdown request (value=2
  - high-voltage shutdown request (value=2
  - wait 0.8 seconds
  - enter state 175
  - fast charging is inactive afterward?
- missing_relations:
  - enter state 155 -> condition judgement
  - condition judgement -> pre-charge failure occurs
  - switch to state 175 -> fast charging is inactive
  - switch to state 175 -> fast charging is inactive
  - shutdown -> high-voltage shutdown request charging/discharging =2
  - high-voltage shutdown request charging/discharging =2 -> wait 0.8s
  - high-voltage shutdown request charging/discharging =2 -> wait 0.8s
  - wait 0.8s -> switch to state 175
- input_excerpt:
  After the system starts up: - If charging is active (charging=1) and the front MCU high-voltage detection flag is 0, transition to state 153. - If the BMS-fast charger handshake flag is 0 and the front MCU high-voltage flag is 0, enter state 155.  While in state 155: 1. If pre-charge failure occurs, move to state 175. If fast charging remains inactive after this, shut down and end the process. 2. If a high-voltage shutdown request (for charging/discharging) is detected (value=2), wait 0.8 seconds before entering state 175. If fast charging is inactive afterward, shut down and end. 3. If the ignition switch status is 2, remain in state 155. If a high-voltage shutdown request (value=2) exists 
- generated_excerpt:
  @startuml start :System starts up; if (charging=1 and front MCU high-voltage detection flag=0?) then (yes)   :Transition to state 153; else (no) endif if (BMS-fast charger handshake flag=0 and front MCU high-voltage flag=0?) then (yes)   :Enter state 155; else (no) endif  switch case (pre-charge failure occurs)   :Move to state 175;   if (fast charging remains inactive?) then (yes)     :Shut down;     end   else (no)   endif case (high-voltage shutdown request (value=2) is detected)   :Wait 0.8 seconds;   :Enter state 175;   if (fast charging is inactive afterward?) then (yes)     :Shut down;     end   else (no)   endif case (ignition switch status is 2)   :Remain in state 155;   if (high-vo
### rac-0004
- dataset: rac
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.5091
- relation_f1: 0.1887
- missing_nodes:
  - slow charging state is 1 and charging/discharging power-up is ready
  - vehicle charging/discharging mode is 2 and power-up is ready
  - switch to state 105
  - condition judgement
  - high-voltage shutdown charging/discharging value is 3 or 4
  - slow charging?
  - slow charging?
  - slow charging?
- extra_nodes:
  - system starts up
  - slow charging is active (state 1
  - vehicle charging/discharging mode is 2 and the system is powered up
  - high-voltage shutdown value is 3 or 4
  - slow charging becomes inactive
  - slow charging becomes inactive
  - slow charging becomes inactive
  - slow charging becomes inactive
- missing_relations:
  - slow charging state is 1 and charging/discharging power-up is ready -> switch to state 95
  - switch to state 95 -> vehicle charging/discharging mode is 2 and power-up is ready
  - vehicle charging/discharging mode is 2 and power-up is ready -> switch to state 105
  - switch to state 105 -> condition judgement
  - condition judgement -> high-voltage shutdown charging/discharging value is 3 or 4
  - high-voltage shutdown charging/discharging value is 3 or 4 -> switch to state 115
  - switch to state 115 -> slow charging?
  - switch to state 115 -> slow charging?
- input_excerpt:
  After the system starts up: - If slow charging is active (state 1) and the charging/discharging system is powered up, switch to state 95. - If the vehicle charging/discharging mode is 2 and the system is powered up, switch to state 105. Then, while in state 105:   1) If the high-voltage shutdown value is 3 or 4, switch to state 115. If slow charging becomes inactive during this, shut down and end the process.   2) If a high-voltage shutdown request (value 3) occurs while the ignition is on (position 2), return to state 105. If the ignition turns off (position 0), switch to state 115. If slow charging becomes inactive, shut down and end.   3) If a pre-charge failure happens, switch to state 1
- generated_excerpt:
  @startuml start :System starts up; switch case (Slow charging is active (state 1) and the charging/discharging system is powered up)   :Switch to state 95; case (Vehicle charging/discharging mode is 2 and the system is powered up)   :Switch to state 105;   switch   case (High-voltage shutdown value is 3 or 4)     :Switch to state 115;     if (Slow charging becomes inactive) then (yes)       :Shut down;       end     endif   case (High-voltage shutdown request (value 3) occurs while the ignition is on (position 2))     :Return to state 105;     if (Slow charging becomes inactive) then (yes)       :Shut down;       end     endif   case (Ignition turns off (position 0))     :Switch to state 115
### lmc-0011
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - system is supported?
  - sensor data is good?
  - autopilot change states from pullup to transition
- extra_nodes:
  - pullup
  - system is supported and sensor data is good?
  - transition
- missing_relations:
  - system is supported? -> sensor data is good?
  - sensor data is good? -> autopilot change states from pullup to transition
- input_excerpt:
  7.	The autopilot shall change states from PULLUP to TRANSITION when the system is supported and sensor data is good.
- generated_excerpt:
  @startuml start :PULLUP; if (System is supported and sensor data is good?) then (yes)   :TRANSITION; else (no) endif @enduml
### lmc-0038
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - for equivalent input of (xt yt)
  - absolute error between zt truth data and output z <= 0.01?
  - allowed
  - not allowed
- extra_nodes:
  - compute absolute error between zt truth data and output z for equivalent input of (xt yt)
  - absolute error <= 0.01?
  - true
  - error tolerance met
  - false
  - error tolerance exceeded
- missing_relations:
  - for equivalent input of (xt yt) -> absolute error between zt truth data and output z <= 0.01?
  - absolute error between zt truth data and output z <= 0.01? -> allowed
  - allowed -> not allowed
- input_excerpt:
  4.	The absolute error between the zt truth data and the output z shall never exceed a tolerance of 0.01, for the equivalent input of (xt, yt).
- generated_excerpt:
  @startuml start :Compute absolute error between zt truth data and output z for equivalent input of (xt, yt); switch (Absolute error <= 0.01?) case (True) :Error tolerance met; case (False) :Error tolerance exceeded; endswitch stop @enduml
### lmc-0056
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - determinant of rotation matrix dcm321
  - =10?
  - allowed
  - not allowed
- extra_nodes:
  - calculate the determinant of the rotation matrix dcm321
  - is dcm321 equal to 1.0?
  - pass requirement
  - fail requirement
- missing_relations:
  - determinant of rotation matrix dcm321 -> =10?
  - =10? -> allowed
  - allowed -> not allowed
- input_excerpt:
  8.	The determinant of the Rotation Matrix, |DCM321|, shall be equal to 1.0.
- generated_excerpt:
  @startuml start :Calculate the determinant of the Rotation Matrix |DCM321|; if (Is |DCM321| equal to 1.0?) then (Yes)   :Pass requirement; else (No)   :Fail requirement; endif stop @enduml
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1569
- relation_f1: 0.0000
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - 1
  - go to promotion jobs home page
  - select the job want to promote
  - 2
  - right-click
  - select source and destination systems
- extra_nodes:
  - promote a joblog into the lifecycle manager tool
  - select the job to promote (or right-click home page and click promote)
  - enter external change management id and click save
  - click edit mappings to create and validate mappings
  - security settings required?
  - select do not promote security (default)
  - promote security
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
  @startuml start :Promote a jobLog into the LifeCycle Manager tool; :Select the job to promote\n(Or right-click home page and click Promote); :Select source and destination systems from drop-down lists; :Enter External Change Management ID and click Save; :Click Mappings; :Click Edit Mappings to create and validate mappings; switch (Security Settings required?) case (Do not Promote Security)   :Select Do not Promote Security (default); case (Promote Security)   :Select Promote Security;   if (Include application rights?) then (Yes)     :Select Include application rights;   endif endswitch :Click View Security to view security dependencies; :Click Test Promote to ensure no CUID conflict; :View
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1633
- relation_f1: 0.0000
- missing_nodes:
  - go to modeling area
  - choose info provider
  - info area displays information
  - transformation
  - data source
  - open data source context menu
  - open data source context menu
  - choose create info package...
- extra_nodes:
  - in the modeling area choose info provider
  - in the context menu of the data source choose create info package...
  - enter a description for the info package and choose save
  - go to the tab page schedule and choose start
  - choose monitor in the toolbar of info package maintenance
  - select the date and choose execute
  - select the load process for your data source from the tree at the left of the screen
  - from the context menu of the data source choose create data transfer process...
- missing_relations:
  - go to data warehousing workbench -> go to modeling area
  - go to modeling area -> choose info provider
  - choose info provider -> info area displays information
  - info area displays information -> transformation
  - transformation -> data source
  - data source -> open data source context menu
  - open data source context menu -> choose create info package...
  - choose create info package... -> enter description
- input_excerpt:
  7.	Loading Transaction Data1. Go to the Data Warehousing Workbench; in the Modeling area choose Info Provider. The transformation and the Data source are displayed in the Info Area below the Info Cube Sales Overview.2. In the context menu of the Data source, choose Create Info Package...3. On the next screen, enter a description for the Info Package and choose Save. The Info Package maintenance screen for the scheduler appears.4. Go to the tab page Schedule and choose Start.5. To check the load process, choose Monitor in the toolbar of Info Package maintenance.6. On the next screen, select the date and choose Execute. The monitor for the load process is displayed.7. Select the load process f
- generated_excerpt:
  @startuml start :Go to the Data Warehousing Workbench; :In the Modeling area choose Info Provider; :In the context menu of the Data source, choose Create Info Package...; :Enter a description for the Info Package and choose Save; :Go to the tab page Schedule and choose Start; :Choose Monitor in the toolbar of Info Package maintenance; :Select the date and choose Execute; :Select the load process for your Data source from the tree at the left of the screen; :Exit the Info Package maintenance screen; :From the context menu of the Data source, choose Create Data Transfer Process...; :Choose Continue; :Go to tab page Extraction and select extraction mode Full; :Activate the data transfer process

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
