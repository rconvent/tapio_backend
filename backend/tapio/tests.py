from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory
from tapio.models import *
from tapio.viewsets import *

# Create your tests here.


class TapioTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):

        # Source 
        cls.s_1 = Source.objects.create(**{
            "names": {
                "fr": "Test source no lifetime"
            },
            "company_id": 1,
            "value": 1.0,
            "emission_factor": 100.0,
            "acquisition_year": 2020,
        })
        cls.s_2 = Source.objects.create(**{
            "names": {
                "fr": "Test source lifetime"
            },
            "company_id": 1,
            "value": 1.0,
            "emission_factor": 100.0,
            "lifetime": 5,
            "acquisition_year": 2020,
        })

        cls.s_3 = Source.objects.create(**{
            "names": {
                "fr": "Test source no acqu. year"
            },
            "company_id": 1,
            "value": 1.0,
            "emission_factor": 100.0,
        })

        # Reduction Strategy
        cls.rs_1 = ReductionStrategy.objects.create(**{
            "names": {"fr" : "Apply raio"},
            "source": cls.s_2
        })
        cls.rs_2 = ReductionStrategy.objects.create(**{
            "names": {"fr" : "Apply ratio"},
            "source": cls.s_3
        })
        cls.rs_3 = ReductionStrategy.objects.create(**{
            "names": {"fr" : "Change EF"},
            "source": cls.s_3
        })
        cls.rs_4 = ReductionStrategy.objects.create(**{
            "names": {"fr" : "Apply ratio and Change EF (same modif)"},
            "source": cls.s_3
        })
        cls.rs_5 = ReductionStrategy.objects.create(**{
            "names": {"fr" : "Apply raio"},
            "source": cls.s_2
        })
        cls.rs_6 = ReductionStrategy.objects.create(**{
            "names": {"fr" : "Change EF (50)"},
            "source": cls.s_2
        })
        cls.rs_6b = ReductionStrategy.objects.create(**{
            "names": {"fr" : "Change EF (80)"},
            "source": cls.s_2
        })
        cls.rs_7 = ReductionStrategy.objects.create(**{
            "names": {"fr" : "Apply ratio and Change EF"},
            "source": cls.s_2
        })
        cls.rs_8 = ReductionStrategy.objects.create(**{
            "names": {"fr" : "first Apply ratio, next year change EF"},
            "source": cls.s_3
        })
        cls.rs_9 = ReductionStrategy.objects.create(**{
            "names": {"fr" : "reduce emission by 10% each year"},
            "source": cls.s_3
        }) 

        # Modification
        Modification.objects.create(**{
            "ratio" : 0.5,
            "effective_year" : 2020,
            "reduction_stategy" : cls.rs_2
        })
        Modification.objects.create(**{
            "emission_factor" : 80,
            "effective_year" : 2020,
            "reduction_stategy" : cls.rs_3
        })
        Modification.objects.create(**{
            "ratio" : 0.5,
            "emission_factor" : 80,
            "effective_year" : 2020,
            "reduction_stategy" : cls.rs_4
        })
        Modification.objects.create(**{
            "ratio" : 0.5,
            "effective_year" : 2021,
            "reduction_stategy" : cls.rs_5
        })
        Modification.objects.create(**{
            "emission_factor" : 50,
            "effective_year" : 2021,
            "reduction_stategy" : cls.rs_6
        })
        Modification.objects.create(**{
            "emission_factor" : 80,
            "effective_year" : 2021,
            "reduction_stategy" : cls.rs_6b
        })
        Modification.objects.create(**{
            "ratio" : 0.5,
            "emission_factor" : 50,
            "effective_year" : 2021,
            "reduction_stategy" : cls.rs_7
        })
        Modification.objects.create(**{
            "ratio" : 0.5,
            "effective_year" : 2021,
            "reduction_stategy" : cls.rs_8
        })
        Modification.objects.create(**{
            "emission_factor" : 50,
            "effective_year" : 2022,
            "reduction_stategy" : cls.rs_8
        })
        Modification.objects.create(**{
            "ratio" : 0.9,
            "effective_year" : 2021,
            "reduction_stategy" : cls.rs_9
        })
        Modification.objects.create(**{
            "ratio" : 0.9,
            "effective_year" : 2022,
            "reduction_stategy" : cls.rs_9
        })
        Modification.objects.create(**{
            "ratio" : 0.9,
            "effective_year" : 2023,
            "reduction_stategy" : cls.rs_9
        })

        cls.r  = Report.objects.create(**{
            "names" : {"fr" : "test"},
            "date": "2023-01-10",
            "year": 2022
        })

        cls.r_2 = Report.objects.create(**{
            "names" : {"fr" : "test"},
            "date": "2023-01-10",
            "year": 2022
        })

        ReportEntry.objects.create(report=cls.r, reduction_strategy=cls.rs_5, scenario="01")
        ReportEntry.objects.create(report=cls.r, reduction_strategy=cls.rs_6b, scenario="02")
        ReportEntry.objects.create(report=cls.r, reduction_strategy=cls.rs_7, scenario="03")

        ReportEntry.objects.create(report=cls.r, reduction_strategy=cls.rs_9, scenario="01")
        ReportEntry.objects.create(report=cls.r, reduction_strategy=cls.rs_9, scenario="02")
        ReportEntry.objects.create(report=cls.r, reduction_strategy=cls.rs_9, scenario="03")

        ReportEntry.objects.create(report=cls.r_2, reduction_strategy=cls.rs_5, scenario="01")
        ReportEntry.objects.create(report=cls.r_2, reduction_strategy=cls.rs_6b, scenario="02")
        ReportEntry.objects.create(report=cls.r_2, reduction_strategy=cls.rs_7, scenario="03")

        ReportEntry.objects.create(report=cls.r_2, reduction_strategy=cls.rs_9, scenario="01")
        ReportEntry.objects.create(report=cls.r_2, reduction_strategy=cls.rs_9, scenario="02")
        ReportEntry.objects.create(report=cls.r_2, reduction_strategy=cls.rs_9, scenario="03")


    def test_sources(self) :
        self.assertEqual(self.s_1.total_emission, 100)
        self.assertEqual(self.s_2.total_emission, 20, msg="Total emission should be divided along the lifetime of the source")


    def test_reduction_strategy_no_modifs(self):

        self.assertEqual(self.rs_1.get_total_emission(year=2020), 20)
        self.assertEqual(self.rs_1.get_total_emission(year=2022), 20)
        self.assertEqual(self.rs_1.get_total_emission(year=2026), 0)


    def test_reduction_strategy_no_lifetime(self):
    
        self.assertEqual(self.rs_2.get_total_emission(year=2020), 50)
        self.assertEqual(self.rs_3.get_total_emission(year=2020), 80)
        self.assertEqual(self.rs_4.get_total_emission(year=2020), 40)


    def test_reduction_strategy_with_lifetime(self):
               
        # before modif lifetime period (should not consider modifications)
        self.assertEqual(self.rs_5.get_total_emission(year=2020), 20)
        self.assertEqual(self.rs_6.get_total_emission(year=2020), 20)
        self.assertEqual(self.rs_7.get_total_emission(year=2020), 20)
        self.assertEqual(self.rs_5.get_delta(year=2020), 0)
        self.assertEqual(self.rs_6.get_delta(year=2020), 0)
        self.assertEqual(self.rs_7.get_delta(year=2020), 0)
        
        # in modif lifetime period and before source ends
        self.assertEqual(self.rs_5.get_total_emission(year=2022), 20+100/5*0.5)
        self.assertEqual(self.rs_6.get_total_emission(year=2022), 20+50/5)
        self.assertEqual(self.rs_7.get_total_emission(year=2022), 20+50/5*0.5)
        self.assertEqual(self.rs_5.get_delta(year=2022), 10)
        self.assertEqual(self.rs_6.get_delta(year=2022), 10)
        self.assertEqual(self.rs_7.get_delta(year=2022), 5)

        # in modif lifetime period and after source ends
        self.assertEqual(self.rs_5.get_total_emission(year=2026), 100/5*0.5)
        self.assertEqual(self.rs_6.get_total_emission(year=2026), 50/5)
        self.assertEqual(self.rs_7.get_total_emission(year=2026), 50/5*0.5)
        # to ask => first source should have 0 so + 10 and not -10?
        self.assertEqual(self.rs_5.get_delta(year=2026), 10)
        self.assertEqual(self.rs_6.get_delta(year=2026), 10)
        self.assertEqual(self.rs_7.get_delta(year=2026), 5)

        # after modif lifetime period
        self.assertEqual(self.rs_5.get_total_emission(year=2030), 0)
        self.assertEqual(self.rs_6.get_total_emission(year=2030), 0)
        self.assertEqual(self.rs_7.get_total_emission(year=2030), 0)
        self.assertEqual(self.rs_5.get_delta(year=2030), 0)
        self.assertEqual(self.rs_6.get_delta(year=2030), 0)
        self.assertEqual(self.rs_7.get_delta(year=2030), 0)

    
    def test_reduction_strategy_no_aqu_year(self):

        # before both modif effective year
        self.assertEqual(self.rs_8.get_total_emission(year=2020), 100)
        # after first modif effective year but befor second
        self.assertEqual(self.rs_8.get_total_emission(year=2021), 100*0.5)
        # after both modif effective year
        self.assertEqual(self.rs_8.get_total_emission(year=2022), 50*0.5)


        # emssion reduction each year 
        self.assertEqual(self.rs_9.get_total_emission(year=2020), 100)
        self.assertEqual(self.rs_9.get_total_emission(year=2021), 100*0.9)
        self.assertEqual(self.rs_9.get_total_emission(year=2022), 100*0.9*0.9)
        self.assertEqual(self.rs_9.get_total_emission(year=2023), 100*0.9*0.9*0.9)
        self.assertEqual(self.rs_9.get_delta(year=2020), 0)
        self.assertEqual(self.rs_9.get_delta(year=2021), 100*0.9-100)
        self.assertEqual(self.rs_9.get_delta(year=2022), 100*0.9*0.9-100)
        self.assertEqual(self.rs_9.get_delta(year=2023), 100*0.9*0.9*0.9-100)


    def test_report(self):  
       
        self.r.save()

        delta_1 = self.r.deltas.get("01", {})
        delta_2 = self.r.deltas.get("02", {})
        delta_3 = self.r.deltas.get("03", {})


        self.assertAlmostEqual(delta_1.get("delta", 0), (10)+(100*0.9*0.9-100))
        self.assertAlmostEqual(delta_2.get("delta", 0), (16)+(100*0.9*0.9-100))
        self.assertAlmostEqual(delta_3.get("delta", 0), (5 )+(100*0.9*0.9-100))

        self.assertAlmostEqual(delta_1.get("initial", 0), (20)+(100))
        self.assertAlmostEqual(delta_2.get("initial", 0), (20)+(100))
        self.assertAlmostEqual(delta_3.get("initial", 0), (20)+(100))

        self.assertAlmostEqual(delta_1.get("modified", 0), (20+10)+(100*0.9*0.9))
        self.assertAlmostEqual(delta_2.get("modified", 0), (20+16)+(100*0.9*0.9))
        self.assertAlmostEqual(delta_3.get("modified", 0), (20+5)+(100*0.9*0.9))

        
    def test_API(self):
        
        user = get_user_model().objects.create(username="admin")
        user.profile.company_id = 1

        client = APIClient(enforce_csrf_checks=False)
        client.force_authenticate(user=user)

        # test sum reports by year
        self.r.save()
        self.r_2.save()
        response = client.get('/api/report/years_emission/?start_year=2022&end_year=2022&scenario=03',  format='json').data
        self.assertEqual(response.get(2023), 240)


        # test sum sources emission by year
        self.s_1.save()
        self.s_2.save()
        self.s_3.save()
        response = client.get('/api/source/years_emission/?acquisition_year_after=2020&end_year_befor=2020',  format='json').data
        print(response)
        



