def test_object_attributes_existence(tester, o, attributes):
    for attribute in attributes:
        tester.assertTrue(hasattr(o, attribute),
                          msg="attribute `{}` not member of `{}`".format(attribute, type(o).__name__))
