# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3791
- node_recall: 0.4549
- node_f1: 0.4136
- relation_precision: 0.3618
- relation_recall: 0.4975
- relation_f1: 0.4189
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7792
- llm_node_recall: 0.7857
- llm_node_f1: 0.7625
- llm_relation_precision: 0.5530
- llm_relation_recall: 0.5605
- llm_relation_f1: 0.5408

## Failure Types
- extra_activity: 19
- extra_or_wrong_relation: 19
- missing_activity: 17
- missing_or_wrong_relation: 15
- wrong_parallel: 2
- wrong_loop: 1

## Representative Failure Cases
### lmc-0035
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.9231
- llm_relation_f1: 0.7692
- missing_nodes:
  - input any value
  - maximum value of nn output z <= 1.1?
  - allowed
  - not allowed
- extra_nodes:
  - receive input values
  - compute nn output z
  - z <= 1.1?
  - accept nn output z
  - enforce z <= 1.1 constraint
- missing_relations:
  - input any value -> maximum value of nn output z <= 1.1?
  - maximum value of nn output z <= 1.1? -> allowed [yes]
  - maximum value of nn output z <= 1.1? -> not allowed [no]
- input_excerpt:
  1.	The maximum value of the NN output, z, shall always be less than or equal to 1.1, regardless of the input values.
- generated_excerpt:
  @startuml start :Receive input values; :Compute NN output z; if (z <= 1.1?) then (yes)   :Accept NN output z; else (no)   :Enforce z <= 1.1 constraint; endif stop @enduml
### pure-0027
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3333
- llm_relation_f1: 0.0000
- missing_nodes:
  - get correlator-backend network interface
  - receive incoming data packets
- extra_nodes:
  - receive incoming data packets from correlator to backend network interface
- missing_relations:
  - get correlator-backend network interface -> receive incoming data packets
- input_excerpt:
  Data Receive – The BE shall receive incoming data packets from the Correlator to Backend network interface. This network is a part of the BE System.
- generated_excerpt:
  @startuml start :Receive incoming data packets from Correlator to Backend network interface; note right: This network is a part of the BE System @enduml
### pure-0054
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1714
- relation_f1: 0.1429
- llm_element_status: success
- llm_node_f1: 0.8500
- llm_relation_f1: 0.7755
- missing_nodes:
  - donor/primary contact has valid donation number
  - arrive at receiving dock
  - see view acquisitions
  - locate donation request
  - see add item to inventory
  - enter information
  - add new item?
  - way to add item
- extra_nodes:
  - donor or primary contact arrives at receiving dock with a valid donation number
  - receiving associate locates donation request in the system
  - how to manage donated item?
  - add a new item to the list by cloning an existing item
  - remove an item by setting the received quantity to zero
  - more items to enter?
  - receiving associate prints a donation receipt
  - write information by hand?
- missing_relations:
  - arrive at receiving dock -> see view acquisitions
  - see view acquisitions -> locate donation request
  - locate donation request -> display donation request information
  - display donation request information -> see add item to inventory
  - see add item to inventory -> enter information
  - enter information -> add new item?
  - add new item? -> way to add item [yes]
  - way to add item -> clone an existing item [case clone]
- input_excerpt:
  1. Donor or Primary Contact arrives at receiving dock with a valid donation number 2. Receiving Associate locates donation request in the system (see View Acquisitions) 3. System displays donation request information 4. Receiving Associate enters information about each donated item into the donation request (see Add Item to Inventory) 4.1. A new item can be added to the list by cloning an existing item 4.2. A new item can be added by clicking the Add Item button 4.3. An item can be removed by setting the received quantity to zero 5. Receiving Associate prints a donation receipt 6. Receiving Associate optionally writes information to the receipt by hand such as condition 7. Donation receipt i
- generated_excerpt:
  @startuml start :Donor or Primary Contact arrives at receiving dock with a valid donation number; :Receiving Associate locates donation request in the system; :System displays donation request information; repeat   switch (How to manage donated item?)   case (Clone existing item)     :Add a new item to the list by cloning an existing item;   case (Click Add Item button)     :Add a new item by clicking the Add Item button;   case (Remove item)     :Remove an item by setting the received quantity to zero;   endswitch repeat while (More items to enter?) is (Yes) ->No; :Receiving Associate prints a donation receipt; if (Write information by hand?) then (Yes)   :Receiving Associate writes informa
### bp-0014
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1935
- relation_f1: 0.0526
- llm_element_status: success
- llm_node_f1: 0.7805
- llm_relation_f1: 0.7391
- missing_nodes:
  - select start
  - select programs
  - select businessobjects xi 3.1
  - select businessobjects enterprise
  - select businessobjects lifecycle manager
  - go to system field
  - enter cms name
  - open authentication drop-down list
- extra_nodes:
  - select start > programs > businessobjects xi 3.1 > businessobjects enterprise > businessobjects lifecycle manager
  - in the system field enter the name of the central management server (cms) on which the lifecycle manager tool is installed
  - select the appropriate authentication method from the authentication drop-down list
  - authentication type
  - enter a user name and a password recognized by the businessobjects enterprise system
  - perform special setup for ldap authentication
  - perform special setup for windows ad authentication
  - perform special setup for third-party authentication
- missing_relations:
  - select start -> select programs
  - select programs -> select businessobjects xi 3.1
  - select businessobjects xi 3.1 -> select businessobjects enterprise
  - select businessobjects enterprise -> select businessobjects lifecycle manager
  - lifecycle manager login screen appears -> go to system field
  - go to system field -> enter cms name
  - enter cms name -> enter username and password
  - enter username and password -> open authentication drop-down list
- input_excerpt:
  14.	log into the LifeCycle Manager tool.To log into the LifeCycle Manager tool, complete the following steps:1. Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager. The LifeCycle Manager login screen appears.2. In the System field, enter the name of the Central Management Server (CMS) on which the LifeCycle Manager tool is installed.3. Enter the user name and password.4. Select the appropriate authentication method from the Authentication drop-down list.The LifeCycle Manager tool supports the following authentication types:• Enterprise authentication - This authentication type requires a user name and a password that are recognize
- generated_excerpt:
  @startuml start :Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager; :The LifeCycle Manager login screen appears; :In the System field, enter the name of the Central Management Server (CMS) on which the LifeCycle Manager tool is installed; :Enter the user name and password; :Select the appropriate authentication method from the Authentication drop-down list; switch (Authentication type) case (Enterprise authentication)   :Enter a user name and a password recognized by the BusinessObjects Enterprise system; case (LDAP authentication)   :Enter a user name and a password recognized by the BusinessObjects Enterprise system;   :Perfor
### bp-0010
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2286
- relation_f1: 0.2105
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.3721
- missing_nodes:
  - click arrows in revenue eld?
  - sort increasing or decreasing
  - click alternative mouse button
  - open context menu
  - choose sort increasing or sort decreasing
  - internet channel is the greatest
  - analyze differences for months?
  - open dropdown box calendar year/month
- extra_nodes:
  - sort method?
  - sort revenue data in increasing or decreasing order
  - choose sort increasing or sort decreasing in context menu
  - observe greatest revenue is obtained with distribution channel internet
  - select 08.2007 in dropdown box calendar year/month
  - select 07.2007 in dropdown box calendar year/month
  - observe revenue data for distribution channel internet increased greatly
  - select 09.2007 in dropdown box calendar year/month
- missing_relations:
  - sort revenue data -> click arrows in revenue eld?
  - click arrows in revenue eld? -> sort increasing or decreasing [yes]
  - click arrows in revenue eld? -> click alternative mouse button [no]
  - sort increasing or decreasing -> internet channel is the greatest [merge]
  - click alternative mouse button -> open context menu
  - open context menu -> choose sort increasing or sort decreasing
  - choose sort increasing or sort decreasing -> internet channel is the greatest [merge]
  - internet channel is the greatest -> analyze differences for months?
- input_excerpt:
  10.	Analyzing Data in the Web Application1. Since you are interested in the revenue, you want to sort the revenue data.2. Click on the arrows in the Revenue eld to sort the revenue data in increasing or decreasing order.3. You can also sort the revenue by clicking the alternative mouse button on Revenue and choosing Sort Sort Increasing or Sort Decreasing in the context menu. You see that the greatest revenue is obtained with the distribution channel Internet.4. To see the differences in the revenue data for the months July, August and September, select rst 08.2007 and then 07.2007 in the dropdown box Calendar Year/Month. You see that the revenue data for the distribution channel Internet in
- generated_excerpt:
  @startuml start :Sort the revenue data; switch (Sort method?) case (Click arrows in Revenue field)   :Sort revenue data in increasing or decreasing order; case (Click alternative mouse button on Revenue)   :Choose Sort Increasing or Sort Decreasing in context menu; endswitch :Observe greatest revenue is obtained with distribution channel Internet; :Select 08.2007 in dropdown box Calendar Year/Month; :Select 07.2007 in dropdown box Calendar Year/Month; :Observe revenue data for distribution channel Internet increased greatly; :Select 09.2007 in dropdown box Calendar Year/Month; :Filter data back to September; :At subtotal of distribution channel Internet (567.308,05), choose Documents Create 
### us-0113
- dataset: us
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.8000
- llm_element_status: success
- llm_node_f1: 0.7273
- llm_relation_f1: 0.3333
- missing_nodes:
  - fail dataset creation
  - stop
- extra_nodes:
  - create dataset
  - dataset creation fails
  - enable dataset for explore
- input_excerpt:
  As a user, I want to ensure that dataset creation fails if the dataset cannot be enabled for explore.
- generated_excerpt:
  @startuml start :Create dataset; if (Dataset can be enabled for explore?) then (No)   :Dataset creation fails; else (Yes)   :Enable dataset for explore; endif @enduml
### pure-0017
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3043
- relation_f1: 0.1379
- llm_element_status: success
- llm_node_f1: 0.5532
- llm_relation_f1: 0.2258
- missing_nodes:
  - leading driver initiate automated request
  - require driver enter train number information?
  - display information entered
  - confirmation?
  - further actions
  - ertms/etcs and radio systems available?
  - driver is required to enter train number?
  - task be carried out once
- extra_nodes:
  - option 1 enter train number
  - show entered train number on display
  - confirm train number
  - option 2 initiate automated request
  - is leading driver?
  - receive train number returned by network
  - driver decision
  - accept
- missing_relations:
  - enter train number -> leading driver initiate automated request
  - leading driver initiate automated request -> register and deregister train number
  - register and deregister train number -> require driver enter train number information?
  - require driver enter train number information? -> display information entered [yes]
  - require driver enter train number information? -> automated request is initiated? [no]
  - display information entered -> confirmation?
  - confirmation? -> further actions [yes]
  - confirmation? -> automated request is initiated? [no]
- input_excerpt:
  5.2.3.26 It shall be possible for the driver to register and deregister a train number in the following ways: 1) enter train number; (M) 2) initiate automated request (applicable only for leading driver). (O) 5.2.3.27 Where the driver is required to enter the train number information, the information entered shall be shown on the display and require confirmation by the driver before further actions are possible. (M) 5.2.3.28 If an automated request is initiated (option 2), the driver shall be able to accept or reject the train number returned by the network. (M) 5.2.3.28i Where ERTMS/ETCS and radio systems are available and the driver is required to enter the train number as part of the init
- generated_excerpt:
  @startuml start switch (Register/deregister train number method) case (Option 1: Enter train number)   :Enter train number;   :Show entered train number on display;   :Confirm train number; case (Option 2: Initiate automated request)   if (Is leading driver?) then (Yes)     :Initiate automated request;     :Receive train number returned by network;     switch (Driver decision)     case (Accept)       :Accept train number;     case (Reject)       :Reject train number;     endswitch   else (No)     stop   endif endswitch  if (ERTMS/ETCS and radio systems available AND entering as part of initialization?) then (Yes)   :Enter train number on ERTMS/ETCS system;   :Transmit entered number to radio
### bp-0002
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3243
- relation_f1: 0.2439
- llm_element_status: success
- llm_node_f1: 0.7111
- llm_relation_f1: 0.6939
- missing_nodes:
  - user authorizations are sufficient?
  - log in
  - choose modeling data warehousing workbench modeling
  - data warehousing workbench is started
  - choose info objects
  - open root node context menu
  - choose create info area
  - enter a description
- extra_nodes:
  - log onto the bi system with a user that has sufficient authorizations
  - start the data warehousing workbench in the sap menu by choosing modeling data warehousing workbench modeling
  - under modeling choose info objects
  - from the context menu at the root node info objects of the info object tree choose create info area
  - enter a technical name and a description for the info area
  - the info area is displayed in the info object tree
  - group your info objects
  - select key figure as the info object type
- missing_relations:
  - user authorizations are sufficient? -> log in [yes]
  - log in -> choose modeling data warehousing workbench modeling
  - choose modeling data warehousing workbench modeling -> data warehousing workbench is started
  - data warehousing workbench is started -> choose info objects
  - info object tree is displayed -> open root node context menu
  - open root node context menu -> choose create info area
  - choose create info area -> enter a technical name [fork]
  - choose create info area -> enter a description [fork]
- input_excerpt:
  2.	Log onto the BI system1.	Log onto the BI system with a user that has sufficient authorizations for executing the scenario.2.	Start the Data Warehousing Workbench in the SAP menu by choosing Modeling Data Warehousing Workbench: Modeling.3.	Under Modeling, choose Info  Objects. The Info  Object tree is displayed.4.	From the context menu at the root node Info Objects of the Info Object tree, choose Create Info Area.5.	On the next screen, enter a technical name and a description for the Info Area. The Info Area is displayed in the Info Object tree.6.	It is used to group your Info Objects.7.	In the context menu of the Info Area, choose Create Info Object Catalog.8.	On the next screen, enter a 
- generated_excerpt:
  @startuml start :Log onto the BI system with a user that has sufficient authorizations; :Start the Data Warehousing Workbench in the SAP menu by choosing Modeling Data Warehousing Workbench: Modeling; :Under Modeling, choose Info Objects; :The Info Object tree is displayed; :From the context menu at the root node Info Objects of the Info Object tree, choose Create Info Area; :Enter a technical name and a description for the Info Area; :The Info Area is displayed in the Info Object tree; :Group your Info Objects; :In the context menu of the Info Area, choose Create Info Object Catalog; :Enter a technical name and description; :Select Key Figure as the Info Object Type; :Choose Create; :Activa
### us-0087
- dataset: us
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.6000
- llm_relation_f1: 0.5000
- missing_nodes:
  - avoid doing timezone conversion
- extra_nodes:
  - view dates and times
  - detect moderator s local timezone
  - convert dates and times to local timezone
- input_excerpt:
  As a moderator, I want to see dates and times in my local timezone, so that I don't have to do timezone conversion myself.
- generated_excerpt:
  @startuml start :View dates and times; :Detect moderator's local timezone; :Convert dates and times to local timezone; :Display dates and times in local timezone; stop @enduml
### pure-0083
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.2308
- llm_element_status: success
- llm_node_f1: 0.7143
- llm_relation_f1: 0.3125
- missing_nodes:
  - display window
  - cancel and return is allowed at any time
  - attempt count <= 3?
  - enter authenticating information
  - user name
  - password
  - validate and establish user privilege
  - successful?
- extra_nodes:
  - display authentication window (entry of user name and password)
  - enter user name and password
  - cancel authentication?
  - authentication successful?
  - authentication unsuccessful and attempts < 3?
- missing_relations:
  - display window -> cancel and return is allowed at any time
  - cancel and return is allowed at any time -> attempt count <= 3?
  - attempt count <= 3? -> enter authenticating information [yes]
  - enter authenticating information -> user name [fork]
  - enter authenticating information -> password [fork]
  - user name -> validate and establish user privilege [merge]
  - password -> validate and establish user privilege [merge]
  - validate and establish user privilege -> authenticate user
- input_excerpt:
  1. The tool displays a window for entry of authenticating information, i.e., user name and password, to validate and establish the privileges of the user. 2. The user enters their user name and password. 3. The tool attempts to authenticate the user and indicates whether authentication has succeeded or not. 4. If authentication is unsuccessful, the user is returned to the authentication window to reenter the information. 5. The tool permits three attempts at authentication before dismissing the authentication window and returning the user to the previous window. 6. The user may cancel the authentication process at any time and return to the previous window.
- generated_excerpt:
  @startuml start :Display authentication window\n(Entry of user name and password); repeat   :Enter user name and password;   if (Cancel authentication?) then (yes)     :Return to previous window;     stop   else (no)     :Attempt to authenticate user;     if (Authentication successful?) then (yes)     else (no)       :Indicate authentication unsuccessful;     endif   endif repeat while (Authentication unsuccessful\nand attempts < 3?) is (yes) ->no; :Indicate authentication succeeded; @enduml
### lmc-0015
- dataset: lmc
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.2222
- missing_nodes:
  - sensor change states from nominal to transition
- extra_nodes:
  - nominal
  - transition
- input_excerpt:
  11.	The sensor shall change states from NOMINAL to TRANSITION when the autopilot is not requesting support (not request).
- generated_excerpt:
  @startuml start :NOMINAL; if (Autopilot is not requesting support (not request)?) then (yes)   :TRANSITION; endif stop @enduml
### lmc-0013
- dataset: lmc
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.5000
- missing_nodes:
  - autopilot change states from standby to maneuver
- extra_nodes:
  - autopilot in standby
  - change state to maneuver
- input_excerpt:
  9.	The autopilot shall change states from STANDBY to MANEUVER when a failure occurs (apfail).
- generated_excerpt:
  @startuml start :Autopilot in STANDBY; if (Failure occurs (apfail)?) then (yes)   :Change state to MANEUVER; else (no) endif @enduml
### bp-0027
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4138
- relation_f1: 0.5333
- llm_element_status: success
- llm_node_f1: 0.8125
- llm_relation_f1: 0.6286
- missing_nodes:
  - experienced expert user?
  - open the promote window
  - click mappings
  - the connection list is displayed
  - select a connection
  - edit in the source system?
  - edited5 is displayed
  - click save or promote
- extra_nodes:
  - click mappings in the promote window
  - the list of federation connections is displayed
  - select a federation connection
  - display the list of properties and their values
  - federation connection edited in the source system?
  - display edited message beside the federation connection
  - user requirement
  - click save
- missing_relations:
  - experienced expert user? -> open the promote window [yes]
  - open the promote window -> click mappings
  - the connection list is displayed -> select a connection
  - edit in the source system? -> edited5 is displayed [yes]
  - edited5 is displayed -> click save or promote
  - edit in the source system? -> click save or promote [no]
  - experienced expert user? -> click save or promote [no]
- input_excerpt:
  27.	map a Federation connection1. In the "Promote" window, click Mappings.2. Click Federation Mappings.The list of Federation connections is displayed.3. Select a Federation connection, and click Edit Federation Connection Properties. The "Edit Federation Connection Properties" tab appears. This tab displays the list of properties and their values.4. Modify the appropriate fields, and click Apply. The "Federation Mappings" tab appears.Note:If you edit a Federation connection in the source system, the followingmessage is displayed beside the federation connection: edited5. Click Save or Promote as per your requirement. Important: Mapping must be performed by an expert user who has adequate kn
- generated_excerpt:
  @startuml start :Click Mappings in the "Promote" window; :Click Federation Mappings; :The list of Federation connections is displayed; :Select a Federation connection; :Click Edit Federation Connection Properties; :The "Edit Federation Connection Properties" tab appears; :Display the list of properties and their values; :Modify the appropriate fields; :Click Apply; :The "Federation Mappings" tab appears; if (Federation connection edited in the source system?) then (yes)   :Display "edited" message beside the federation connection; else (no) endif switch (User requirement) case (Save)   :Click Save; case (Promote)   :Click Promote; endswitch stop @enduml
### rac-0005
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4878
- relation_f1: 0.5417
- llm_element_status: success
- llm_node_f1: 0.9434
- llm_relation_f1: 0.7586
- missing_nodes:
  - switch to state 95
  - power-up is ready and vehicle charging/discharging mode is 2
  - condition judgement
  - remote mode is closed
  - shutdown
  - pet mode open request is closed
- extra_nodes:
  - system starts up
  - move to state 95
  - power-up readiness is confirmed and vehicle s charging/discharging mode is set to 2?
  - proceed to state 105
  - case condition
  - go to state 105
  - slow charging becomes inactive?
  - shift to state 28
- missing_relations:
  - switch to state 93 -> charging/discharging power-up is active and front mcu high-voltage detection flag is 1
  - switch to state 95 -> power-up is ready and vehicle charging/discharging mode is 2
  - switch to state 105 -> condition judgement
  - switch to state 28 -> remote mode is closed
  - switch to state 28 -> pet mode open request is closed
  - pet mode open request is closed -> shutdown [yes]
  - switch to state 105 -> soc reaches 80 and dcdc state is 3
- input_excerpt:
  After the system starts up: - If slow charging is active and the front MCU high-voltage detection flag is 0, transition to state 93. - If charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1, move to state 95. - When power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2, proceed to state 105.  Then handle these cases: 1. In remote mode: Go to state 105. If slow charging becomes inactive, shift to state 28. Should remote mode deactivate, initiate shutdown and terminate. 2. Upon receiving a pet mode request: Enter state 105. If slow charging is inactive, transition to state 28. After processing the pet mode request, p
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active\nand front MCU high-voltage\ndetection flag is 0?) then (yes)   :Transition to state 93; elseif (Charging/discharging power-up is active\nand front MCU high-voltage\ndetection flag is 1?) then (yes)   :Move to state 95; elseif (Power-up readiness is confirmed\nand vehicle's charging/discharging\nmode is set to 2?) then (yes)   :Proceed to state 105; endif switch (Case condition) case (Remote mode)   :Go to state 105;   if (Slow charging becomes inactive?) then (yes)     :Shift to state 28;   endif   if (Remote mode deactivates?) then (yes)     :Initiate shutdown;     stop   endif case (Pet mode request received)   :Enter state 10
### rac-0006
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.3889
- llm_element_status: success
- llm_node_f1: 0.8421
- llm_relation_f1: 0.8444
- missing_nodes:
  - condition judgement
  - remote mode is enabled
  - shutdown
  - pet mode request handling is finished
  - battery soc is 20
  - battery soc reaches 80 and dcdc state is 3
- extra_nodes:
  - system starts up
  - condition?
  - enter state 110
  - slow charging becomes inactive?
  - go to state 28
  - shut down and end
  - move to state 28
  - soc reaches 80 and dcdc state is 3?
- missing_relations:
  - enter power-up mode -> condition judgement
  - condition judgement -> remote mode is enabled [case 1]
  - remote mode is enabled -> switch to state 110
  - switch to state 28 -> remote mode is disabled
  - condition judgement -> pet mode request is received [case 2]
  - pet mode request is received -> switch to state 110
  - condition judgement -> battery soc is 20 [case 3]
  - battery soc is 20 -> switch to state 110
- input_excerpt:
  After the system starts up: If slow charging is active, go into power-up mode. Then: 1.  If remote mode is enabled, enter state 110. Then, if slow charging becomes inactive, go to state 28. Finally, if remote mode is disabled, shut down and end. 2.  If a pet mode request comes in, switch to state 110. Then, if slow charging is inactive, move to state 28. Once the pet mode request is handled, shut down and end. 3.  If the battery SOC is 20, enter state 110. Then, if slow charging is inactive, switch to state 28. If the SOC later reaches 80 and the DCDC state is 3, shut down and end.
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active?) then (yes)   :Go into power-up mode;   switch (Condition?)   case (Remote mode is enabled)     :Enter state 110;     if (Slow charging becomes inactive?) then (yes)       :Go to state 28;     endif     if (Remote mode is disabled?) then (yes)       :Shut down and end;       stop     endif   case (Pet mode request comes in)     :Switch to state 110;     if (Slow charging is inactive?) then (yes)       :Move to state 28;     endif     :Pet mode request is handled;     :Shut down and end;     stop   case (Battery SOC is 20)     :Enter state 110;     if (Slow charging is inactive?) then (yes)       :Switch to state 28;     endif   
### lmc-0003
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5714
- relation_f1: 0.3333
- llm_element_status: success
- llm_node_f1: 0.9091
- llm_relation_f1: 0.6000
- missing_nodes:
  - determine selected value
- extra_nodes:
  - two good branches available?
  - determine selected value using good channel average
- missing_relations:
  - in single fail state -> a good channel average of the remaining two good branches
- input_excerpt:
  [RM-003] In the single fail state, a good channel average of the remaining two good branches shall be used to determine the selected value.
- generated_excerpt:
  @startuml start :Enter single fail state; if (Two good branches available?) then (yes)   :Calculate good channel average of the remaining two good branches;   :Determine selected value using good channel average; else (no) endif stop @enduml
### rac-0016
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6275
- relation_f1: 0.6761
- llm_element_status: success
- llm_node_f1: 0.9286
- llm_relation_f1: 0.9767
- missing_nodes:
  - enter state 186
  - condition judgement
  - after 2.2s timeout?
  - fast charging is inactive and bms counter=1
  - shutdown
  - battery soc=80 and dcdc state=3
- extra_nodes:
  - system starts up
  - switch to state 186
  - condition evaluation
  - fast charging becomes inactive?
  - wait for 2.2-second timeout
  - bms counter changes to 1?
  - switch directly to state 12
  - shut down
- missing_relations:
  - enter state 186 -> condition judgement
  - fast charging is inactive and bms counter=1 -> switch to state 12 [yes]
  - switch to state 12 -> ignition switch=0
  - switch to state 12 -> ignition switch=0 and fast charging is disabled
  - switch to state 12 -> remote mode is disabled
  - switch to state 12 -> pet mode ends
  - switch to state 12 -> battery soc=80 and dcdc state=3
  - battery soc=80 and dcdc state=3 -> shutdown [yes]
- input_excerpt:
  After the system starts up, if fast charging is active, it enters the power-up state. Then, if the high-voltage shutdown request is 2, it switches to state 186. In state 186, the behavior depends on several conditions: First, if the ignition switch is 2 and the BMS counter is 2, it stays in state 186. After that, if fast charging becomes inactive, it waits for a 2.2-second timeout before switching to state 12. Alternatively, if the BMS counter changes to 1, it switches directly to state 12. Then, if the ignition switch becomes 0, it shuts down, resets the BMS counter, and exits. Second, if the ignition switch is 2 and the onboard charger command is 0, it remains in state 186; if the command 
- generated_excerpt:
  @startuml start :System starts up; if (Fast charging active?) then (yes)   :Enter power-up state;   if (High-voltage shutdown request is 2?) then (yes)     :Switch to state 186;     switch (Condition evaluation)     case (First)       if (Ignition switch is 2\nand BMS counter is 2?) then (yes)         :Stay in state 186;         if (Fast charging becomes inactive?) then (yes)           :Wait for 2.2-second timeout;           :Switch to state 12;         elseif (BMS counter changes to 1?) then (yes)           :Switch directly to state 12;         endif         if (Ignition switch becomes 0?) then (yes)           :Shut down;           :Reset BMS counter;           :Exit;           stop        
### us-0097
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.2857
- llm_element_status: success
- llm_node_f1: 0.7143
- llm_relation_f1: 0.3333
- extra_nodes:
  - account available?
  - retry sign up
  - publish data package under publisher account
- missing_relations:
  - sign up for an account -> get publisher account
- input_excerpt:
  As a Publisher, I want to sign up for an account, so that that I can publish my data package to the registry and to have a publisher account to publish my data package under.
- generated_excerpt:
  @startuml start :Sign up for an account; if (Account available?) then (yes)   :Create publisher account; else (no)   :Retry sign up;   stop endif :Publish data package to the registry; :Publish data package under publisher account; stop @enduml
### rac-0007
- dataset: rac
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8205
- relation_f1: 0.6400
- llm_element_status: success
- llm_node_f1: 0.6842
- llm_relation_f1: 0.2308
- missing_nodes:
  - shutdown
  - flag becomes 2
- extra_nodes:
  - system starts up
  - what condition is met?
  - which sub-condition is met?
  - shut down
  - high-voltage shutdown request flag becomes 2?
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request charging/discharging flag is 2
  - flag becomes 0 and cp duty cycle is 85 -> switch to state 126 [yes]
  - bms self-check counter is 1 -> battery pre-heating is required [no]
  - flag becomes 0 and cp duty cycle is 85 -> flag becomes 0 and bms self-check counter is 1 [no]
  - high-voltage shutdown request charging/discharging flag is 2 -> central control command is 2 and vehicle is not in charging/discharging mode [no]
  - switch to state 110 -> flag becomes 2
  - flag becomes 2 -> switch to state 115 [yes]
- input_excerpt:
  After the system starts up, if slow charging is active, we enter power-up mode. Then:  1) When the high-voltage shutdown request (charging/discharging) flag is 2, switch to state 115. After switching:    a. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If the BMS self-check counter shows 1, switch to state 130. If slow charging becomes inactive, shut down and end.    b. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If battery pre-heating is required, switch to state 130. If slow charging becomes inactive, shut down and end.    c. If the flag drops to 0 while the BMS self-check counter is 1, switch to state 126. If CP duty cycle hits 85% with 
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging active?) then (yes)   :Enter power-up mode;   switch (What condition is met?)   case (High-voltage shutdown request flag is 2)     :Switch to state 115;     switch (Which sub-condition is met?)     case (Flag drops to 0 with CP duty cycle at 85%)       :Switch to state 126;       if (BMS self-check counter shows 1?) then (yes)         :Switch to state 130;       endif     case (Flag drops to 0 with CP duty cycle at 85%)       :Switch to state 126;       if (Battery pre-heating is required?) then (yes)         :Switch to state 130;       endif     case (Flag drops to 0 while BMS self-check counter is 1)       :Switch to state 126;       if 

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
