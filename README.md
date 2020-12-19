# Gmail Filter 
========== - Gmail Filter - Ver 1.0 - ==========

A basic email filter for Gmail.
Has the ability to automatically star, trash, archive, flag, or read any email you want, as long as it's cotained within the Gmail messaging service.
Can be used to do any action you want to any email after almost any given amount of time.

Keep in mind that this filter is a simple project, and is still in the works. It will grow more efficient and feature rich over time.


========== - Version 1.1 - Public Release ==========

- Efficientcy slightly improved.

- Keeps track of the subject, from line, and nick name of filtered emails as well as when they were fitered in a seperate text document.

- dded the Email object, as well as a list of filtered Email objects as a basis for future features.

- Added the 'counter' and 'nuke' functions.

- Improved code readability.

- Released publically.


========== - Version 1.2 - Added Logging and Naming Scheme ==========

- Added a naming scheme for objects created in the program according to the following list:

Lists: lowercase_with_underscores

Dicts: lowercase_with_underscores + Dict

Strings: initially-Lowercase-With-Hypens

Classes: Capitalized

Funcs: initiallyLowercase + Func


- Added logging for errors, using the Error.log file.

- Added the 'Error' Class for emails which had undergone a UnicodeDecodingError.

- Added a list for 'Error' objects, titled 'email_class.'

- The time during which an email was filtered is now an attribute of both 'Email' and 'Error' objects.
