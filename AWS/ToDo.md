 - Make the instantiate module more OO;

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

 - Move tests into their own subfolder.

 - look into using imagebuilder as a way to bake-in certain post-facto
   features to any cherry-picked AMI:
   - set GRUB_TIMEOUT=30 in /etc/default/grub;
   - create the "somebody" account, for console access;
   - install the SSM agent (done implicitly by ImageBuilder);
   - install the CloudWatch agent (using AWS-provided recipe);

 - [DONE] Create an instance that uses ARM (Graviton?).  See why it
   balks at UEFI.
   - it didn't balk at UEFI, it just had a problem with a mismatch - I
     changed the architecture of the image, but forgot to change the
     instance type to match;

 - [DONE] Make a library module for spinning-up a new instance.

 - [DONE] Create some basic roles and instance-profiles which have a
   minimum set of policies to allow contact with SSM and CloudWatch.
