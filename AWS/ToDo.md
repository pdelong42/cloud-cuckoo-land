 - Make a library module for spinning-DOWN a new instance.

 - Write a script to check for console access, and enable it if it's
   not already:

   response = client.get_serial_console_access_status()
   print( dumps( response, default = str ) )

   response = client.enable_serial_console_access()
   print( dumps( response, default = str ) )

 - I should fork ConsoleToInstance() into two versions:
   InteractiveConsoleToInstance() and RecordConsoleToFile(); or
   perhaps instead make a more general class which optionally writes
   to a file.

 - Fix the escape sequence that breaks-out of the SSH session.  It
   should start with a newline, but right now it's just a tilde
   followed by a dot.

 - It looks like the console logic can't handle UTF-8.  Fix that.  It
   breaks when I run `lsblk` in the console of the instance.

 - Create separate test cases for Amazon Linux and for RHEL (and maybe
   Fedora too).

 - Create an instance and a VPC that only use IPv6.

 - Create an instance that uses Fedora.

 - Create an instance that uses ARM (Graviton?).  See why it balks at
   UEFI.

 - Move tests into their own subfolder.

 - [DONE] Make a library module for spinning-up a new instance.

 - [DONE] Create some basic roles and instance-profiles which have a
   minimum set of policies to allow contact with SSM and CloudWatch.
