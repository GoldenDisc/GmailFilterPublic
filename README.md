# Gmail Filter 
A basic email filter for Gmail.
Has the ability to automatically star, trash, archive, flag, or read any email you want, as long as it's cotained within the Gmail messaging service.
Can be used to do any action you want to any email after almost any given amount of time.

GOOGLE DRIVE DOWNLOAD LINK FOR THE NEEDED GMAIL API PACKAGE: ***TO BE ADDED***


========== - Version 1.3 - Added Flexibility and Commenting - ==========

- Changed and updated formatting

- Converted the 'filterFunc' function into a 'Filter' class. The functionality of the filter itself is now much more flexable.

- The code previously responsible for connecting to the Gmail servers has been condensed into the 'connectFunc' function.

- 'Cut the fat' around a few smaller parts of the program.

- Updated the names of a few parts of the program to better reflect their usage.

- Now allows the user to much more easily change the URL given to the SCOPES variable, which in turn changes the permissions the program has when interacting with the
Gmail servers.

- Additionally includes a list of all possible modifiers for the SCOPES variable, and how they change the permissions of the program.

- All modules taken from the Gmail API website and are vital for the useage of the program when connecting to and interacting with the Gmail servers have now been 
condensed into a simple downloadable package. Now you don't have to go through the pain of using Pip and manually grabbing the files for the program to use 
like I did!

- Majorly increased the amount of comments present in the program. Essentially every part of the program, as well as how they interact with other parts of the program, is now 
fully explained within the code itself.


Keep in mind that this filter is a simple project, and is still in the works. It will grow more efficient and feature rich over time.


========== - Version 1.2 - Added Logging and Naming Scheme - ==========

- Added a naming scheme for objects created in the program according to the following list:

Lists: lowercase_with_underscores

Dicts: lowercase_with_underscores + Dict

Classes: Capitalized

Class Instances: initiallyLowercase

Funcs: initiallyLowercase + Func


- Added logging for errors, using the Error.Log file.

- Added the 'Error' Class for emails which had undergone a UnicodeDecodingError.

- Added a list for 'Error' objects, titled 'error_class.'

- The time during which an email was filtered is now an attribute of both 'Email' and 'Error' objects.


========== - Version 1.1 - Public Release - ==========

- Efficientcy slightly improved.

- Keeps track of the subject, from line, and nick name of filtered emails as well as when they were fitered in a seperate text document.

- Added the Email object, as well as a list of filtered Email objects as a basis for future features.

- Added the 'counter' and 'nuke' functions.

- Improved code readability.

- Released publically.


