# TeamSpeak Server Query Commands

This markdown table lists the available commands for interacting with a TeamSpeak server via the server query interface. The table includes the command name and a brief description of its functionality.

| Command| Description|
|---------|------|
|apikeyadd|create a apikey|
|apikeydel|delete a apikey|
|apikeylist|list apikeys|
|banadd|create a ban rule|
|banclient|ban a client|
|bandel|delete a ban rule|
|bandelall|delete all ban rules|
|banlist|list ban rules on a virtual server|
|bindinglist|list IP addresses used by the server instance|
|channeladdperm|assign permission to channel|
|channelclientaddperm|assign permission to channel-client combi|
|channelclientdelperm|remove permission from channel-client combi|
|channelclientpermlist|list channel-client specific permissions|
|channelcreate|create a channel|
|channeldelete|delete a channel|
|channeldelperm|remove permission from channel|
|channeledit|change channel properties|
|channelfind|find channel by name|
|channelgroupadd|create a channel group|
|channelgroupaddperm|assign permission to channel group|
|channelgroupclientlist|find channel groups by client ID|
|channelgroupcopy|copy a channel group|
|channelgroupdel|delete a channel group|
|channelgroupdelperm|remove permission from channel group|
|channelgrouplist|list channel groups|
|channelgrouppermlist|list channel group permissions|
|channelgrouprename|rename a channel group|
|channelinfo|display channel properties|
|channellist|list channels on a virtual server|
|channelmove|move channel to new parent|
|channelpermlist|list channel specific permissions|
|clientaddperm|assign permission to client|
|clientdbdelete|delete client database properties|
|clientdbedit|change client database properties|
|clientdbfind|find client database ID by nickname or UID|
|clientdbinfo|display client database properties|
|clientdblist|list known client UIDs|
|clientdelperm|remove permission from client|
|clientedit|change client properties|
|clientfind|find client by nickname|
|clientgetdbidfromuid|find client database ID by UID|
|clientgetids|find client IDs by UID|
|clientgetnamefromdbid|find client nickname by database ID|
|clientgetnamefromuid|find client nickname by UID|
|clientgetuidfromclid|find client UID by client ID|
|clientinfo|display client properties|
|clientkick|kick a client|
|clientlist|list clients online on a virtual server|
|clientmove|move a client|
|clientpermlist|list client specific permissions|
|clientpoke|poke a client|
|clientsetserverquerylogin|set own login credentials|
|clientupdate|set own properties|
|complainadd|create a client complaint|
|complaindel|delete a client complaint|
|complaindelall|delete all client complaints|
|complainlist|list client complaints on a virtual server|
|custominfo|display custom client properties|
|customsearch|search for custom client properties|
|customset|add or update a custom client property.|
|customdelete|remove a custom client property.|
|ftcreatedir|create a directory|
|ftdeletefile|delete a file|
|ftgetfileinfo|display details about a file|
|ftgetfilelist|list files stored in a channel filebase|
|ftinitdownload|init a file download|
|ftinitupload|init a file upload|
|ftlist|list active file transfers|
|ftrenamefile|rename a file|
|ftstop|stop a file transfer|
|gm|send global text message|
|help|read help files|
|hostinfo|display server instance connection info|
|instanceedit|change server instance properties|
|instanceinfo|display server instance properties|
|logadd|add custom entry to log|
|login|authenticate with the server|
|logout|deselect virtual server and log out|
|logview|list recent log entries|
|messageadd|send an offline message|
|messagedel|delete an offline message from your inbox|
|messageget|display an offline message from your inbox|
|messagelist|list offline messages from your inbox|
|messageupdateflag|mark an offline message as read|
|permfind|find permission assignments by ID|
|permget|display client permission value for yourself|
|permidgetbyname|find permission ID by name|
|permissionlist|list permissions available|
|permoverview|display client permission overview|
|permreset|delete all server and channel groups and restore default permissions|
|privilegekeyadd|creates a new privilege key|
|privilegekeydelete|delete an existing privilege key|
|privilegekeylist|list all existing privilege keys on this server|
|privilegekeyuse|use a privilege key|
|queryloginadd|add a query client login|
|querylogindel|remove a query client login|
|queryloginlist|list all query client logins|
|quit|close connection|
|sendtextmessage|send text message|
|servercreate|create a virtual server|
|serverdelete|delete a virtual server|
|serveredit|change virtual server properties|
|servergroupadd|create a server group|
|servergroupaddclient|add client to server group|
|servergroupaddperm|assign permissions to server group|
|servergroupautoaddperm|globally assign permissions to server groups|
|servergroupautodelperm|globally remove permissions from server group|
|servergroupclientlist|list clients in a server group|
|servergroupcopy|create a copy of an existing server group|
|servergroupdel|delete a server group|
|servergroupdelclient|remove client from server group|
|servergroupdelperm|remove permissions from server group|
|servergrouplist|list server groups|
|servergrouppermlist|list server group permissions|
|servergrouprename|rename a server group|
|servergroupsbyclientid|get all server groups of specified client|
|serveridgetbyport|find database ID by virtual server port|
|serverinfo|display virtual server properties|
|serverlist|list virtual servers|
|servernotifyregister|register for event notifications|
|servernotifyunregister|unregister from event notifications|
|serverprocessstop|shutdown server process|
|serverrequestconnectioninfo|display virtual server connection info|
|serversnapshotcreate|create snapshot of a virtual server|
|serversnapshotdeploy|deploy snapshot of a virtual server|
|serverstart|start a virtual server|
|serverstop|stop a virtual server|
|servertemppasswordadd|create a new temporary server password|
|servertemppassworddel|delete an existing temporary server password|
|servertemppasswordlist|list all existing temporary server passwords|
|setclientchannelgroup|set a clients channel group|
|tokenadd|alias for privilegekeyadd|
|tokendelete|alias for privilegekeydelete|
|tokenlist|alias for privilegekeylist|
|tokenuse|alias for privilegekeyuse|
|use|select virtual server|
|version|display version information|
|whoami|display current session info|
