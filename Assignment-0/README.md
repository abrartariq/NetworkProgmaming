# Programming Assignment 0: Intro to Python and Git

**This assignment is due at 23:55 CDT on Thursday, September 3.**

This assignment has three purposes:

  1. [To give you some practice using git](#using-git-section),
  2. [To get python 3.8 installed on your system](#intro-to-python-section), and
  3. [To do some basic tasks in python 3.8 to make sure you're familiar with the language's basic syntax and features](#assignment-section).

## <a name="using-git-section"></a>Using Git and GitHub
In this course you will use [git](https://git-scm.com/) to
receive and submit your homework assignments.  We'll be using
[GitHub](https://github.com/) to manage all of the code provided to you, and the homework assignments you submit.

### What are Git and GitHub?
Git is a popular, open source version control system. It helps you keep track
of changes to your files, and helps you collaborate with others.
GitHub provides several conveniences on top of git (a web interface, stores
a remote copy of your code, manages access for you etc.).  Git and GitHub are
complementary, not supplementary, tools.

A full introduction to git is beyond the scope of this document, but there are
[many](https://guides.github.com/activities/hello-world/)
[good](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)
[guides](https://www.git-tower.com/learn/git/ebook/en/command-line/basics/what-is-version-control#start)
on the web that will be helpful for learning git.  For this class you will
need to understand the [clone](https://www.git-scm.com/docs/git-clone),
[add](https://www.git-scm.com/docs/git-add),
[commit](https://www.git-scm.com/docs/git-commit) and
[push](https://www.git-scm.com/docs/git-push)
commands in git.

Git is a complicated, powerful system, but learning it is valuable and worth
the time you put into it.


### Getting Git
Git may already be installed on your machine.  If it is not, you will need to
download and install git, either from the [git](https://git-scm.com/) website,
from your linux distribution, or wherever else is most convenient.

All instructions in this course will be given using the command line version
of git.  Students wishing to use GUI tools will be responsible for learning
them on their own.  You are strongly encouraged to use the command line version
of git.


### Using Git in This Course
Assignments will be given to you in git "repositories", or code collections
that you will modify with your solutions and then resubmit.  Git tracks
directories (and sub-directories), not individual files.  When you commit
your assignment for grading, you will be submitting an entire directory tree
in git for grading, not just certain files.

In general, you will follow the below pattern when using git.

```bash
# First you will copy the git repo containing the assignment to your local
# machine.  This will give you a complete local copy of the project.
# This will create a directory on your machine, along with some files.
git clone <URL to git project>

# You will need to change and add to the files in the directory, so that
# the entire directory matches how you'd like to submit your assignment
# for grading.
cd <project directory>
... (editing the files to complete your assignment)

# Once you're ready to send your work for grading.  This will generally take
# three steps:
#
#   First, "add" the changes you'd like to send to the server.
#   In most cases, this will be all the files in the directory.
#   The "-A" in the below example tells git to also keep track of where you
#   deleted a file, and the "." means "everything in the current directory"
#   and below.
git add -A .

#   Second, "commit" the changes, telling git "ok, treat all the changes
#   I've "added" far together, I'm getting them ready to send to the
#   server".  The "-m" means "I'm going to add a message to this set of
#   changes, so that I'll know what they're about in the future".
git commit -m "completed homework 0"

#   Third and last, "push" the changes back to the server.  This tells git
#   "I've made some changes to the code, I want you to make the code on the
#   server match my local version".
git push
```

Git is extremely powerful, and you may need to access other parts of its
functionality in this class, but in general, the above example covers
the most common git use cases.


### When Git "Breaks"
When you're first learning git, its very easy to get your repository into
a state where it seems "broken", and the system isn't acting in a way
you understand.  When this happens, you might find the best thing to do
is to stop trying to "fix" things, and instead:

 1. back up your work to a different directory,
 2. delete your existing repo from your local machine,
 3. clone a clean copy of the repo,
 4. copy your work back into the repo, and
 5. commit and push your work in your new, "clean" repo.

While the above steps aren't a good long term strategy for using git,
they can get you out of a bind while you're still learning the tools.


## <a name="intro-to-python-section"></a>Intro to Python
This class requires the current version of python, **Python 3.8**.  Please
make sure that you are using Python 3.8 for all assignments.  Python 3
is similar to Python 2, but the two are incompatible in many ways.
Programs that work on Python 2 may not work on Python 3.  You will be
responsible for making sure your assignments work with Python 3.8.

If you're unsure what version of python you are using, you can always check
by typing `python --version` on the command line.

Python is a popular, dynamic, memory managed language.  It has many features
that make it easier to work with than other languages.
If you're already familiar with python, feel free to
skip over this section.  For those new to the language, this section
provides an overview of some of the unique features of the language.


### Getting Python
You should make sure you have Python 3.8 installed on
your computer.  You can get python by going to the
[Python website](https://www.python.org/), going to the download section,
and installing the appropriate download.

If you're using linux, you might find it faster to use the package manager
for your linux distribution to get python (again, making sure it is the
correct version).  If you're using OSX and have a system like
[homebrew](http://brew.sh/) installed, you can use that to easily install
Python 3.8.

You are responsible for getting Python 3.8 installed.  If you have
any questions or problems, please contact the TA.


### Syntax
If you're used to languages like C and Java, python might look a little alien.
This is because python does not use curly braces (`{` or `}`) to denote
the end of blocks, or semi-colons to denote the end of lines.  Instead, Python
relies on white space.

```c
// In C you end up repeating yourself a lot, indenting things and wrapping
// blocks in curly braces.
void a_function(int * firstArg, int * secondArg) {
    // You also repeat yourself, but using both ";" and new lines
    // to mark the end of a line of code.
    int firstInt = 1;
    int secondInt = 2;
}
```

```python
# In Python, you type less, and have less redundancy.  You
# may find that this reduces the number of errors you make, and makes
# your programs easier to maintain.
def a_function(first_arg, second_arg):
    first_int = 1
    second_int = 2
```

### Dynamic Types
Languages like Java and C require you to declare types in function signatures
and variable declarations.  If, for example, you're writing a program C, you
and you want to declare a variable to be an integer, and another variable to
be a character, you need to do something like the following:

```c
#include <stdio.h>

// Defining some variables in C
int myInt = 3;
char someChar = 'a';

// Defining a function in C
int some_function(int anInt, char aChar) {
    printf("Here is the integer I was given: %d\n", anInt);
    printf("And here is the character I was given: %c\n", aChar);
    return 0;
}

// C programs always start with the main function
int main(int argc, char * argv[]) {
    // Calling a function in C
    some_function(myInt, someChar);
}
```

In most ways, python is much less strict about types.  You don't specify a
type when you declare a variable, and variables can take on values of any type,
even changing over the lifetime of your program.  The below, for example,
is valid python code:

```python
# Defining some variables in python.  Note that we don't define any
# types, python does that automatically.
my_int = 3
some_char = "a"

# Defining a function in python.  Note that you don't declare types
# for the arguments in python, the language handles that for you.
# We also don't have to declare a return type, thats handled automatically
# too.
def some_function(an_int, a_char):
    print("Here is the integer I was given:", an_int)
    print("And here is the character I was given:", a_char)

some_function(my_int, some_char)
```


### Native Data Structures
Python provides many conveniences for defining and working with data structures
compared to languages like Java and C.  Python doesn't
allow you to do anything you can't do in Java and C, Python makes it much
easier, and much less error prone, to interact with structures like arrays
(which python calls *lists*), hash tables (which python calls *dicts*), and
sets (which python calls... *sets*).

```python
# In python, you can define an array (or, in python terms, a list) of
# variables in line, and then loop over them easily.  The below code
# creates a list / array of three strings, and then prints them all out.
list_of_strings = ["first", "second", "third"]

# Python provides this short hand syntax for iterating over each element
# in a list.  In C, you might use a for loop and index into each element
# in the list.
#
# The below list will print out the following text:
#
#   first
#   second
#   third
for a_string in list_of_strings:
    print(a_string)

# We can do the same thing with a hash table, or a mapping of values
# to values.  The below code maps the names of numbers (as strings) to
# their actual value (as integers).
number_mapping = {
    "one": 1,
    "two": 2,
    "three": 3,
}

# Now we loop over each item in the hash table (or dict) we created,
# which will produce the following lines (though the order is
# unpredictable).
#
#   one can also be written as 1
#   two can also be written as 2
#   three can also be written as 3
for string_version, int_version for number_mapping.items():
    print(string_version, "can also be written as", int_version)
```


### Large Standard Library
Python comes with a large standard library, and includes "out of the box"
a large amount of functionality to help you complete common tasks.
This is true compared to Java, and *especially* compared to C. This reduces the
amount of third party code you need in Python to complete common tasks.

A full list of all the functionality included in the
[python standard library](https://docs.python.org/3.8/library/index.html)
can be found online.


### Other Python Features
The above just scratches the surface of what makes python an interesting
and useful language.  Python has powerful object oriented tools like Java,
closures and anonymous functions like Lisp and JavaScript, and
a full module system for structuring your code and taking advantage of code
written by others.

You wont be using most of these features in this class,
but they're in the language and it will benefit you to learn more about them
as you become more familiar with the language.


### Writing Better Python
There are great tools to help you become a better python programmer, and to
help you write better, cleaner, less-bug-laden code.  Its highly recommended
that you use these tools, and they can help you catch, fix and prevent errors,
and write code that will be easier to understand if you ever need to revist
them (plus, if you ever use any of these assignments as code samples in a job
application, its a good thing to show that you're familiar with and already
following python best practices.

One tool is [pep8](https://pep8.readthedocs.io/en/release-1.7.x/), a command
line tool that checks that your code is following python formatting and style
best practices.  Making that your code is well formatted will make it easier
to understand, revisit, revise, and help you avoid
[subtle errors](https://gotofail.com/).  You should check that your
code matches the `pep8` style wherever possible.

[pylint](https://www.pylint.org/) is another code quality tool.  It checks
that your code is well documented, well formatted, and avoids practices
that can make your code confusing and fragile.  You should also consider
using `pylint` to check all the python code you submit in this course.

For this assignment, using `pep8` and `pylint` is not required, just highly
recommended.  However, it may be required on future assignments.  Please
familiarize yourself with these tools as soon as possible.


## <a name="assignment-section"></a>Assignment
The goal of this assignment is to test your use of basic git features,
that you have Python 3.8 installed on your system, and that you're familiar with
the basics of the language.


### <a name="programming-assignment-description"></a>Programming
Once you have python installed, write a python program that prints out the
following things, one on each line:

 1. Your email address.
 2. Your name, as a list, with each part of your name as a different string
    in a list.  So, for the TA, it would be the result of printing a list
    with two strings in it, "hamidreza" and "almasi".  Please use
    all lower case characters.
 3. The current date and time, matching the following format:
    `2020-08-27 04:05:13.073277`. (in otherwise, with the year, then the month,
    then the date, followed by the current hour, minute, second and
    millisecond).
 4. Define a function called `four` that takes three arguments, `start`, `stop`,
    and `step`.  The function should assume that each argument will be an
    integer.  This function should return a list of integers, starting at
    the `start` integer, and increasing by the `step` integer, up to but
    **not including** the `stop` integer.

    For example, if I called `four(10, 50, 10)`, the function should return
    the list `[10, 20, 30, 40]` (note that 50 is not included).

    Similarly, if I called `four(2, 9, 3)`, the function should return
    `[2, 5, 8]`.

    Print the result of calling your `four` function with the arguments 17, 40,
    and 6 (ie `print(four(17, 40, 6))`).
 5. The current version of python.


### Hints and Notes
For **number 2**, your program should give results of printing the list with
the parts of your name in it.  No need to do any fancy string formatting
or anything like that.  Just use the `print` function on the list of strings.

Similarly, for **number 3**, you must determine the current date and time using python.
*Do not* hard code something into your code.  The
[datetime](https://docs.python.org/3.8/library/datetime.html#datetime.datetime.now)
module will be helpful.

For **number 4**, you can use any function or functionality in the python
standard library to help you in this task, even ones that have
[very similar functionality](https://docs.python.org/3.8/library/functions.html#func-range).
Just make sure that you are returning a list. **Bonus hint**, you can convert
from a [range](https://docs.python.org/3.8/library/functions.html#func-range)
to a `list` (which the homework requires) using
[list](https://docs.python.org/2/library/functions.html#func-list). Make
sure your function is returning a `list` to receive credit.

For **number 5**, *do not* hard code the version of python into your code (i.e. do
not write `print("3.8")`).  You must use the python system for printing the
current version to receive credit.  The [sys](https://docs.python.org/3.8/library/sys.html#sys.version)
module will be helpful.

Also for **number 5**, depending on your environment, python might print your
python version on more than one line.  That is not a problem.


### Testing Your Program
You should test your program before submitting it.  In python, this is as
simple as running `python hw0.py` (or, depending on your platform
and environment, possibly `python3 hw0.py`).


### Submission and Grading
You must submit your solution to this assignment through git.  When you submit
your assignment, your project should have (at least) the following three files
in it:

  * `README.md`: this file
  * `hw0.py`: your solution to this homework assignment
  * `netid.txt`: a text file that contains only your UIC NetID.  It should not
    contain anything else.

There are a total of **10 possible points** for this assignment.

  * **5 points** for having your UIC Net ID in the `netid.txt` file.
  * **1 point** for each of the 5 problems in the
    [Programming Assignment Description](#programming-assignment-description)
    section, when executing `hw0.py`.

There is no partial credit for any problem.  Other files in your repository
will be ignored.

**This assignment is due at 23:55 CDT on Thursday, September 3.**
