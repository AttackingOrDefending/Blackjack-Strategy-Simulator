"""Test the basic strategy generator."""
from basic_strategy_generator import draw_and_export_tables


def test_basic_strategy() -> None:
    """Test the basic strategy generator."""
    draw_and_export_tables(0, filename="basic_strategy_generated_during_testing.csv", plot_results=False)
    with open("basic_strategy_generated_during_testing.csv") as file:
        test_contents = file.read()
    correct_contents = """n4,h,h,h,h,h,h,h,h,h,h
n5,h,h,h,h,h,h,h,h,h,h
n6,h,h,h,h,h,h,h,h,h,h
n7,h,h,h,h,h,h,h,h,h,h
n8,h,h,h,h,h,h,h,h,h,h
n9,h,dh,dh,dh,dh,h,h,h,h,h
n10,dh,dh,dh,dh,dh,dh,dh,dh,h,h
n11,dh,dh,dh,dh,dh,dh,dh,dh,dh,h
n12,h,h,s,s,s,h,h,h,h,h
n13,s,s,s,s,s,h,h,h,h,h
n14,s,s,s,s,s,h,h,h,h,h
n15,s,s,s,s,s,h,h,h,uh,h
n16,s,s,s,s,s,h,h,uh,uh,uh
n17,s,s,s,s,s,s,s,s,s,s
n18,s,s,s,s,s,s,s,s,s,s
n19,s,s,s,s,s,s,s,s,s,s
n20,s,s,s,s,s,s,s,s,s,s
n21,s,s,s,s,s,s,s,s,s,s
a12,h,h,h,h,dh,h,h,h,h,h
a13,h,h,h,dh,dh,h,h,h,h,h
a14,h,h,h,dh,dh,h,h,h,h,h
a15,h,h,dh,dh,dh,h,h,h,h,h
a16,h,h,dh,dh,dh,h,h,h,h,h
a17,h,dh,dh,dh,dh,h,h,h,h,h
a18,s,ds,ds,ds,ds,s,s,h,h,h
a19,s,s,s,s,s,s,s,s,s,s
a20,s,s,s,s,s,s,s,s,s,s
a21,s,s,s,s,s,s,s,s,s,s
s2,p,p,p,p,p,p,h,h,h,h
s3,p,p,p,p,p,p,h,h,h,h
s4,h,h,h,p,p,h,h,h,h,h
s5,dh,dh,dh,dh,dh,dh,dh,dh,h,h
s6,p,p,p,p,p,h,h,h,h,h
s7,p,p,p,p,p,p,h,h,h,h
s8,p,p,p,p,p,p,p,p,p,p
s9,p,p,p,p,p,s,p,p,s,s
s10,s,s,s,s,s,s,s,s,s,s
s11,p,p,p,p,p,p,p,p,p,p
"""
    assert test_contents == correct_contents
