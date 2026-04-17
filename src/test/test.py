from main.pre_processer.pre_processer import PreProcesser


def test():
    print("Running tests...")

    s = """  
say 1
if (a):
    say 2
    if (b):
        say 3
    say 4
    if (c):
        say 5

        say 6
say 7
   

   
    """

    pre_processer_test = PreProcesser(s)
    pre_processer_test.run()
    print(pre_processer_test.data)

if __name__ == "__test__":
    test()
