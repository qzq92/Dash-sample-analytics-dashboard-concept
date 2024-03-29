# Simple analytics enabled dashboard with (near) real-time information on weather, carpark and traffic conditions.

## Acknowledgement

### Data sources

All data are retrieved via API calls to data.gov.sg accessible [here](https://beta.data.gov.sg/). Key data sources involved are as follows:
1. Traffic camera
2. Weather data (Temperature and rainfall)
3. Taxi location data

For developers, please refer to the link [here](https://guide.data.gov.sg/developers) on possible deprecation and updates on API and other information.


## Introduction

## What does this app show

Work in progress. To be determined.

## Screenshots of app
- To be updated

## Built with following:
* [Dash](https://dash.plot.ly/) - Main server and interactive components 
* [Plotly Python](https://plot.ly/python/) - Used to create the interactive plots
* [Dash DAQ](https://dash.plot.ly/dash-daq) - Styled technical components for industrial applications

### Supported by following APIs/tokens (you will need to register an account to get access tokens for use):

Please refer to the provided link for more information
* [LTA DataMall API Access](https://datamall.lta.gov.sg/content/datamall/en.html) - Various API supplying transportation related data
* [OneMap API](https://www.onemap.gov.sg/apidocs/) - API used for generating train/mrt stations and its exits data
* [Mapbox](https://docs.mapbox.com/api/overview/) - API used for embedding Mapbox in web app.

## Requirements
We suggest you to create an Anaconda environment using the requirements.yml file provided, and install all of the required dependencies listed within.  In your Terminal/Command Prompt:

```
git clone https://github.com/plotly/Dash-sample-analytics-dashboard-concept.git
cd Dash-sample-analytics-dashboard-concept
conda create -f requirements.txt
```

If you prefer to install all of the required packages in your own Anaconda environment, simply activate your own Anaconda environment and execute the following command with your activated environment:

```
pip install -r requirements.txt
```

and all of the required `pip` packages, will be installed, and the app will be able to run.


## Using this application

Run this app locally by:
```
python app.py
```
Open http://0.0.0.0:8050/ in your browser, you will see an interactive dashboard.

## Other miscellaneous information

### Traffic Camera ID geolocations information as of 13 Dec 2022.

|ID|Lat|Lon|Description of Location|
|---|---|---|---|
|1001|1.29531332|103.871146|ECP/MCE/KPE instersection|
|1002|1.319541067|103.8785627|PIE(Tuas) exit road to KPE(MCE)|
|1003|1.323957439|103.8728576|PIE(Changi) exit road to KPE(TPE)|
|1004|1.319535712|103.8750668|PIE(Changi) exit to KPE(TPE)/Sims Way|
|1005|1.363519886|103.905394|KPE(TPE) Defu Flyover|
|1006|1.357098686|103.902042|KPE(MCE) Tunnel Entrance| 
|1501|1.274143944|103.8513168|Straits Boulevard to MCE|
|1502|1.271350907|103.8618284|Slip Road to MCE from Marina Link|
|1503|1.270664087|103.8569779|MCE(KPE) near Slip road to Central Boulevard|
|1504|1.294098914|103.8760562|Slip Road from ECP(Sheares) to MCE(AYE)|
|1505|1.275297715|103.8663904|Slip Road from Marina Coastal Drive to MCE(KPE)|
|1701|1.323604823|103.8587802|CTE Whampoa River|
|1702|1.34355015|103.8601984|CTE Braddell Flyover|
|1703|1.328147222|103.8622033|CTE Whampoa Flyover|
|1704|1.285693989|103.8375245|CTE/Chin Swee Road|
|1705|1.375925022|103.8587986|CTE Ang Mo Kio Flyover|
|1706|1.38861|103.85806|CTE Yio Chu Kang Flyover|
|1707|1.280365843|103.8304511|AYE(Tuas) Jalan Bukit Merah Exit|
|1709|1.313842317|103.845603|CTE(AYE) Cavenagh Exit|
|1711|1.35296|103.85719|CTE Ang Mo Kio South Flyover|
|2701|1.447023728|103.7716543|Causeway|
|2702|1.445554109|103.7683397|BKE Entrance after Causeway|
|2703|1.350477908|103.7910336|BKE/PIE Intersection|
|2704|1.429588536|103.769311|BKE Woodlands Flyover|
|2705|1.36728572|103.7794698|BKE Dairy Farm Flyover|
|2706|1.414142|103.771168|BKE Between Turf Club and Mandai Road exits|
|2707|1.3983|103.774247|BKE Between KJE and Mandai Road exits|
|2708|1.3865|103.7747|BKE(Woodlands) before Slip road to KJE|
|3702|1.33831|103.98032|ECP/PIE(Changi) Intersection|
|3704|1.295855016|103.8803147|ECP(Changi)/Slip Road from MCE to ECP(Changi)|
|3705|1.32743|103.97383|ECP(Sheares) Before Xilin Ave exit|
|3793|1.309330837|103.9350504|ECP Laguna Flyover|
|3795|1.301451452|103.9105963|ECP Marina Parade Flyover|
|3796|1.297512569|103.8983019|ECP Tanjong Katong Flyover|
|3797|1.295657333|103.885283|ECP Tanjong Rhu Flyover|
|3798|1.29158484|103.8615987|ECP Benjamin Sheares Bridge over Raffles Boulevard|
|4701|1.2871|103.79633|AYE Before Portsdown Flyover|
|4702|1.27237|103.8324|AYE Keppel Viaduct|
|4703|1.348697862|103.6350413|AYE After Tuas Checkpoint|
|4704|1.27877|103.82375|AYE Lower Delta Flyover|
|4705|1.32618|103.73028|AYE(MCE) after Yuan Ching Road Exit|
|4706|1.29792|103.78205|AYE(Tuas) After Buona Vista Flyover|
|4707|1.333446481|103.6527008|AYE(MCE) beside Jalan Ahmad Ibrahim|
|4708|1.29939|103.7799|AYE(MCE) beside Singapore Institute of Technology|
|4709|1.312019|103.763002|AYE(Tuas) before Exit to Clementi Ave 6|
|4710|1.32153|103.75273|AYE Pandan River Flyover|
|4712|1.341244001|103.6439134|AYE Jalan Ahmad Ibrahim slip road entrance/exit|
|4713|1.347645829|103.6366955|AYE Before Tuas Checkpoint|
|4714|1.31023|103.76438|AYE(Tuas) After Clementi Flyover|
|4716|1.32227|103.67453|AYE(Tuas) After Benoi Flyover|
|4798|1.259999997|103.8236111|Sentosa Gateway to Harbourfront|
|4799|1.260277774|103.8238889|Sentosa Gateway (Entrance/Exit to Sentosa)|
|5794|1.3309693|103.9168616|PIE(Tuas) After Bedok North Flyover|
|5795|1.326024822|103.905625|PIE Eunos Flyover|
|5797|1.322875288|103.8910793|PIE Paya Lebar Flyover|
|5798|1.320360781|103.8771741|PIE Aljunied West Flyover|
|5799|1.328171608|103.8685191|PIE Woodsville Flyover|
|6701|1.329334|103.858222|PIE(Tuas) Exit to Kim Keat Link|
|6703|1.328899|103.84121|PIE Thomson Flyover|
|6704|1.326574036|103.8268573|PIE Mount Pleasant Flyover|
|6705|1.332124|103.81768|PIE(Changi) after Adam Flyover|
|6706|1.349428893|103.7952799|PIE(Changi) after BKE exit|
|6708|1.345996|103.69016|PIE Nanyang Flyover|
|6710|1.344205|103.78577|PIE(Changi) Anak Bukit Flyover|
|6711|1.33771|103.977827|PIE(Changi) Exit from ECP|
|6712|1.332691|103.7702788179709|PIE(Tuas) before slip road to Clementi Ave 6|
|6713|1.340298|103.945652|PIE(Tuas) after Tampines South Flyover|
|6714|1.361742|103.703341|PIE(Changi) exit to KJE(BKE)
|6715|1.356299|103.716071|PIE Hong Kah Flyover|
|6716|1.322893|103.6635051|AYE/PIE Tuas Flyover|
|7791|1.354245|103.963782|TPE Upper Changi Flyover|
|7793|1.37704704|103.9294698|TPE Api Api Flyover|
|7794|1.37988658|103.9200917|TPE(SLE) slip road to KJE|
|7795|1.38432741|103.915857|TPE(Changi) after Halus Bridge|
|7796|1.39559294|103.9051571|TPE(SLE) before Punggol Flyover|
|7797|1.40002575|103.8570253|TPE/Seletar West Link Intersection|
|7798|1.39748842|103.8540047|TPE(SLE) exit to SLE|
|8701|1.38647|103.74143|KJE Choa Chu Kang West Flyover|
|8702|1.39059|103.7717|KJE Gali Batu Flyover|
|8704|1.3899|103.74843|KJE(BKE) After Choa Chu Kang Dr|
|8706|1.3664|103.70899|PIE(Tuas) Slip Road to KJE|
|9701|1.39466333|103.834746|SLE Lentor Flyover|
|9702|1.39474081|103.8179709|SLE Upper Thomson Flyover|
|9703|1.422857|103.773005|SLE/BKE Interchange|
|9704|1.42214311|103.7954206|SLE Ulu Sembawang Flyover|
|9705|1.42627712|103.7871664|SLE Marsiling Flyover|
|9706|1.41270056|103.8064271|SLE Mandai Lake Flyover|

## Setup

Work in progress

## Background
Work in progress

## Problem statement

Work in progress

## Summary of Findings & Recommendations

Work in progress