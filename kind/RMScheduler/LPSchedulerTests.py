import unittest
from LPScheduler import *

class LPSchedulerTests(unittest.TestCase):
    def test_blank_input(self):
        cluster_state = {
            "list_of_nodes": [],
            "list_of_pods": [],
            "pod_to_node": dict(),
            "num_nodes": 0,
            "num_pods": 0,
            "node_resources": dict(),
            "pod_resources": dict(),
        }
        scheduler = LPScheduler(cluster_state)
        scheduler.make_schedule()
        solution = scheduler.scheduler_tasks["sol"]
        self.assertEqual(solution, [])

    def test_follows_criticality_order(self):
        cluster_state = {
            "list_of_nodes": ["n0"],
            "list_of_pods": ["p0", "p1", "p2", "p3"],
            "pod_to_node": dict(),
            "num_nodes": 1,
            "num_pods": 4,
            "node_resources": {"n0": 4},
            "pod_resources": {"p0": 4, "p1": 1, "p2": 1, "p3": 1},
        }
        scheduler = LPScheduler(cluster_state)
        scheduler.make_schedule()
        solution = scheduler.scheduler_tasks["sol"]
        self.assertEqual(solution, [])

    # I don"t actually know if the answers are optimal, but they"re the answers
    # I got with the first version of the LP so this will at least ensure that
    # the LP hasn"t changed
    def test_very_complex_examples(self):
        # 10 nodes, 100 pods, nodes 40-80, pods 5-10 (pods aren't supposed to fit in aggregate in this test)
        cluster_state = {
            "list_of_nodes": ["n0", "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9"],
            "list_of_pods": ["p0", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p25", "p26", "p27", "p28", "p29", "p30", "p31", "p32", "p33", "p34", "p35", "p36", "p37", "p38", "p39", "p40", "p41", "p42", "p43", "p44", "p45", "p46", "p47", "p48", "p49", "p50", "p51", "p52", "p53", "p54", "p55", "p56", "p57", "p58", "p59", "p60", "p61", "p62", "p63", "p64", "p65", "p66", "p67", "p68", "p69", "p70", "p71", "p72", "p73", "p74", "p75", "p76", "p77", "p78", "p79", "p80", "p81", "p82", "p83", "p84", "p85", "p86", "p87", "p88", "p89", "p90", "p91", "p92", "p93", "p94", "p95", "p96", "p97", "p98", "p99"],
            "pod_to_node": {"p1": "n1"},
            "num_nodes": 10,
            "num_pods": 100,
            "node_resources": {"n0": 58, "n1": 58, "n2": 76, "n3": 62, "n4": 40, "n5": 78, "n6": 76, "n7": 65, "n8": 43, "n9": 40},
            "pod_resources": {"p0": 10, "p1": 10, "p2": 10, "p3": 8, "p4": 7, "p5": 8, "p6": 9, "p7": 10, "p8": 9, "p9": 10, "p10": 6, "p11": 10, "p12": 5, "p13": 9, "p14": 7, "p15": 6, "p16": 6, "p17": 9, "p18": 7, "p19": 6, "p20": 7, "p21": 8, "p22": 8, "p23": 7, "p24": 9, "p25": 6, "p26": 7, "p27": 8, "p28": 6, "p29": 10, "p30": 10, "p31": 7, "p32": 6, "p33": 8, "p34": 10, "p35": 5, "p36": 6, "p37": 9, "p38": 5, "p39": 6, "p40": 5, "p41": 9, "p42": 9, "p43": 8, "p44": 6, "p45": 9, "p46": 6, "p47": 5, "p48": 7, "p49": 5, "p50": 8, "p51": 8, "p52": 10, "p53": 10, "p54": 9, "p55": 7, "p56": 6, "p57": 6, "p58": 10, "p59": 9, "p60": 5, "p61": 7, "p62": 8, "p63": 5, "p64": 5, "p65": 9, "p66": 6, "p67": 5, "p68": 10, "p69": 10, "p70": 9, "p71": 5, "p72": 6, "p73": 5, "p74": 7, "p75": 7, "p76": 5, "p77": 6, "p78": 10, "p79": 8, "p80": 10, "p81": 6, "p82": 9, "p83": 10, "p84": 5, "p85": 7, "p86": 5, "p87": 7, "p88": 10, "p89": 9, "p90": 5, "p91": 6, "p92": 7, "p93": 6, "p94": 10, "p95": 9, "p96": 9, "p97": 6, "p98": 10, "p99": 6}
        }
        scheduler = LPScheduler(cluster_state)
        scheduler.make_schedule()
        solution = scheduler.scheduler_tasks["sol"]
        self.assertEqual(solution, [("n0", "p12"), ("n0", "p17"), ("n0", "p26"), ("n0", "p42"), ("n0", "p60"), ("n0", "p61"), ("n0", "p66"), ("n0", "p69"), ("n1", "p8"), ("n1", "p15"), ("n1", "p30"), ("n1", "p39"), ("n1", "p58"), ("n1", "p64"), ("n1", "p74"), ("n1", "p76"), ("n2", "p3"), ("n2", "p11"), ("n2", "p23"), ("n2", "p33"), ("n2", "p38"), ("n2", "p47"), ("n2", "p52"), ("n2", "p54"), ("n2", "p57"), ("n2", "p62"), ("n3", "p0"), ("n3", "p9"), ("n3", "p21"), ("n3", "p27"), ("n3", "p28"), ("n3", "p32"), ("n3", "p40"), ("n3", "p43"), ("n4", "p1"), ("n4", "p34"), ("n4", "p46"), ("n4", "p70"), ("n4", "p71"), ("n5", "p13"), ("n5", "p14"), ("n5", "p22"), ("n5", "p24"), ("n5", "p36"), ("n5", "p41"), ("n5", "p49"), ("n5", "p55"), ("n5", "p63"), ("n5", "p78"), ("n6", "p4"), ("n6", "p6"), ("n6", "p7"), ("n6", "p16"), ("n6", "p20"), ("n6", "p29"), ("n6", "p35"), ("n6", "p53"), ("n6", "p56"), ("n6", "p72"), ("n7", "p25"), ("n7", "p31"), ("n7", "p45"), ("n7", "p50"), ("n7", "p65"), ("n7", "p67"), ("n7", "p68"), ("n7", "p73"), ("n7", "p77"), ("n8", "p2"), ("n8", "p5"), ("n8", "p18"), ("n8", "p37"), ("n8", "p59"), ("n9", "p10"), ("n9", "p19"), ("n9", "p44"), ("n9", "p48"), ("n9", "p51"), ("n9", "p75”)])

if __name__ == "__main__":
    unittest.main()
