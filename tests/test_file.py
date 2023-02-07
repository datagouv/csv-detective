from csv_detective import explore_csv
import os

def test_routine_on_file():
    output_profile=True
    output = explore_csv.routine(csv_file_path="tests/a_test_file.csv",
        num_rows=-1,
        output_profile=output_profile,
        save_results=False
    )
    assert isinstance(output, dict)
    assert output['separator']==';'
    assert output['header_row_idx']==2
    assert output['header']==["NUMCOM","NOMCOM","NUMDEP","NOMDEP","NUMEPCI","NOMEPCI","TXCOUVGLO_COM_2014","TXCOUVGLO_DEP_2014","TXCOUVGLO_EPCI_2014","STRUCTURED_INFO","GEO_INFO"]
    assert output['total_lines']==414
    assert output['nb_duplicates']==7
    assert output['columns']['NOMCOM']['format']=='commune'
    assert output['columns']['NOMDEP']['format']=='departement'
    assert output['columns']['NUMEPCI']['format']=='siren'
    assert output['columns']['STRUCTURED_INFO']['python_type']=='json'
    assert output['columns']['STRUCTURED_INFO']['format']=='json'
    assert output['columns']['GEO_INFO']['python_type']=='json'
    assert output['columns']['GEO_INFO']['format']=='json_geojson'
    assert output['columns']['NUMEPCI']['format']=='siren'

    if output_profile:
        assert all([c in list(output['profile']['NUMCOM'].keys()) for c in ["min","max","mean","std","tops","nb_distinct","nb_missing_values"]])
