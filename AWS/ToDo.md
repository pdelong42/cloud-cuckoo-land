 - Write a script to check for console access, and enable it if it's
   not already:

   response = client.get_serial_console_access_status()
   print( dumps( response, default = str ) )

   response = client.enable_serial_console_access()
   print( dumps( response, default = str ) )

 - I should fork ConsoleToInstance() into two versions:
   InteractiveConsoleToInstance() and RecordConsoleToFile()

 - Fix the escape sequence that breaks-out of the SSH session.  It
   should start with a newline, but right now it's just a tilde
   followed by a dot.

 - Create some basic roles and instance-profiles which have a minimum
   set of policies to allow contact with SSM and CloudWatch.
