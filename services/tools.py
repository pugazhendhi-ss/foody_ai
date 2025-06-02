from langchain.tools import Tool


def add_numbers(query: str):
    nums = [int(x) for x in query.split() if x.isdigit()]
    print(f"AI using func, proof ---> {nums}")
    return str(sum(nums))

add_tool = Tool(
    name="Calculator",
    func=add_numbers,
    description="Use this if you need to add the numbers, if input has 2 numbers."
)



