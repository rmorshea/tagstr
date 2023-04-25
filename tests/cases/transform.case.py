# GIVEN: no f-string
func @ "hello"
# EXPECT: no transformation
func @ "hello"
# END

# GIVEN: f-string no interpolation
func @ f"hello"
# EXPECT: transform to call with string
func ( 'hello', )
# END

# GIVEN: f-string with interpolation
func @ f"hello {name}"
# EXPECT: transform to call with string and thunk
func ( 'hello ',(lambda:(name),'name',None,None), )
# END

# GIVEN: f-string with interpolation and suffix
func @ f"hello {name}!"
# EXPECT: transform to call with string, thunk, string
func ( 'hello ',(lambda:(name),'name',None,None),'!', )
# END

# GIVEN: multiline expression
(
    func @ f"hello"
)
# EXPECT: preserve lines
(
    func ( 'hello', )
)
# END

# GIVEN: multiline f-string
func @ f"""
hello
"""
# EXPECT: preserve lines
func ( '\nhello\n', )\
\
# END

# GIVEN: f-string with added string
func @ f"hello" + "something-else"
# EXPECT: ignore added string
func ( 'hello', )+"something-else"
# END

# GIVEN: multiline f-string with added string
func @ f"""
hello
""" + "something-else"
# EXPECT: ignore added string
func ( '\nhello\n', )\
\
    + "something-else"
# END
