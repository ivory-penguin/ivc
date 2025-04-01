"""
so we don't want to store the encryption key in plaintext
so to avoid this we have to do an 8 step process (never look into secure programming ever):
 - make sure the cpython will work
 - write a C++ source file 
    - use extern "C" {} to make CPython support C++
    - make it generate the encryption key at runtime rather than have it be stored in the program
    - make sure that the cpp can't seg fault or anything ever under any circumstances or we have to do this all again
 - create a setup.py file to compile the .cpp into machine code properly
 - run python setup.py build_ext --inplace to create the .pyd (win) or .so (unix), ideally do both for cross platform support
 - setup os verification an use importlib to dynamically import the .so and .pyd depending on your environment because no pip here
 - should now be possible to import from python cross platform if all goes well, otherwise go all the way back to step 2 (don't do it wrong)
 - immediately destroy the key after access, never store it for any longer than needed to avoid memory dump attacks or at least make them really annoying to perform

this is absolutely not worth
"""