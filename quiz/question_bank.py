FALLBACK_QUESTIONS = {
    "python": {
        "easy": [
            {
                "question": "What keyword is used to define a function in Python?",
                "answer": "def",
                "hint": "It is a three-letter keyword used before the function name.",
            },
            {
                "question": "What built-in function prints output to the console in Python?",
                "answer": "print",
                "hint": "You use it with parentheses in modern Python.",
            },
            {
                "question": "Which keyword is used to import a module in Python?",
                "answer": "import",
                "hint": "It appears at the beginning of many files.",
            },
            {
                "question": "What value represents nothing or no value in Python?",
                "answer": "none",
                "hint": "It starts with a capital letter in Python code.",
            },
            {
                "question": "Which Python collection stores key value pairs?",
                "answer": "dictionary",
                "hint": "It is often shortened to dict.",
            },
            {
                "question": "Which loop iterates over items in a sequence in Python?",
                "answer": "for loop",
                "hint": "It often starts with the word for.",
            },
        ],
        "medium": [
            {
                "question": "What built-in Python function returns the length of a list?",
                "answer": "len",
                "hint": "It is a short three-letter function.",
            },
            {
                "question": "Which keyword is used to create a class in Python?",
                "answer": "class",
                "hint": "It is written right before the class name.",
            },
            {
                "question": "What symbol is commonly used for floor division in Python?",
                "answer": "double slash",
                "hint": "It uses two forward slash characters.",
            },
            {
                "question": "Which statement is used to handle exceptions in Python?",
                "answer": "try except",
                "hint": "It begins with try and catches errors.",
            },
            {
                "question": "Which keyword creates an anonymous function in Python?",
                "answer": "lambda",
                "hint": "It is often used for short inline functions.",
            },
            {
                "question": "What special method initializes a new object in Python?",
                "answer": "__init__",
                "hint": "It runs when an object is created.",
            },
        ],
        "hard": [
            {
                "question": "Which Python feature allows a function to yield values one at a time?",
                "answer": "generator",
                "hint": "It often uses the yield keyword.",
            },
            {
                "question": "What decorator is commonly used to define a method on the class rather than the instance?",
                "answer": "classmethod",
                "hint": "Its name starts with class.",
            },
            {
                "question": "What mechanism lets one object customize attribute access dynamically in Python?",
                "answer": "__getattr__",
                "hint": "It is a dunder method for missing attributes.",
            },
            {
                "question": "What Python structure is used to manage context with the with statement?",
                "answer": "context manager",
                "hint": "It controls setup and cleanup around a block.",
            },
            {
                "question": "Which Python concept lets a nested function remember variables from an outer scope?",
                "answer": "closure",
                "hint": "It captures surrounding state.",
            },
            {
                "question": "What protocol method makes an object iterable in Python?",
                "answer": "__iter__",
                "hint": "It returns an iterator.",
            },
        ],
    },
    "java": {
        "easy": [
            {
                "question": "Which keyword is used to define a class in Java?",
                "answer": "class",
                "hint": "It appears right before the class name.",
            },
            {
                "question": "What method is commonly used to print text in Java?",
                "answer": "system out println",
                "hint": "It ends with println.",
            },
            {
                "question": "Which primitive type stores true or false values in Java?",
                "answer": "boolean",
                "hint": "It has the same name as the concept.",
            },
            {
                "question": "Which keyword is used to create an object in Java?",
                "answer": "new",
                "hint": "It is a short word used before a constructor.",
            },
            {
                "question": "What symbol ends most Java statements?",
                "answer": "semicolon",
                "hint": "It looks like a dot with a comma tail.",
            },
            {
                "question": "Which keyword refers to the current object instance in Java?",
                "answer": "this",
                "hint": "It is a four-letter keyword.",
            },
        ],
        "medium": [
            {
                "question": "Which keyword is used to inherit from a class in Java?",
                "answer": "extends",
                "hint": "It connects a child class to a parent class.",
            },
            {
                "question": "What is the entry point method of a Java application?",
                "answer": "main",
                "hint": "It is the method the JVM looks for first.",
            },
            {
                "question": "Which collection in Java does not allow duplicate values?",
                "answer": "set",
                "hint": "It is an interface often implemented by HashSet.",
            },
            {
                "question": "Which access modifier makes a member available everywhere?",
                "answer": "public",
                "hint": "It is the most open access modifier.",
            },
            {
                "question": "Which keyword prevents a method from being overridden in Java?",
                "answer": "final",
                "hint": "It also prevents reassignment for variables.",
            },
            {
                "question": "What exception handling block is used after try in Java?",
                "answer": "catch",
                "hint": "It handles the thrown exception.",
            },
        ],
        "hard": [
            {
                "question": "Which Java annotation marks a method as intentionally replacing a parent implementation?",
                "answer": "override",
                "hint": "It starts with the at symbol in code.",
            },
            {
                "question": "What Java mechanism removes the need to manually free memory in most applications?",
                "answer": "garbage collection",
                "hint": "It automatically reclaims unused objects.",
            },
            {
                "question": "Which Java concept allows one interface or class to work with different data types safely?",
                "answer": "generics",
                "hint": "It often uses angle brackets.",
            },
            {
                "question": "What Java keyword is used so only one thread can execute a block or method at a time?",
                "answer": "synchronized",
                "hint": "It is used for thread safety.",
            },
            {
                "question": "Which Java reference type can represent the absence of an object and often causes runtime errors if used carelessly?",
                "answer": "null",
                "hint": "It leads to a common pointer exception.",
            },
            {
                "question": "What JVM area stores per-thread method execution frames?",
                "answer": "stack",
                "hint": "Each method call pushes a frame onto it.",
            },
        ],
    },
}
