# Income Inequality and Human Capital - Lab Experiment
 ## Real Effort Task and Investment
This App is part of the experiment by *Villamizar(2018)*. It introduces the
competition for higher wages as a Tullock Contest. 

The first part of the experiment introduces the Real Effort
Task as a Letter Counting Task. You can access it here: https://github.com/djhernanv/Tullock_Income_Intro

If you want to use this experiment in full or in part for your own purposes, feel free to do so.
Just make sure you quote *Villamizar(2018)*.


### Installation

1. In Terminal or PowerShell go to your oTree folder, for instance ```cd oTree```, 
and create the folder for the app with ```mkdir Tullock_Income_RET``` .
1. Make sure you have "numpy" installed with ```pip install numpy``` or ```pip3 install numpy``` if you use Python 3.
1. Define the App in settings.py with:
~~~
  INSTALLED_APPS = ['otree',
                  'django.contrib.humanize',
                  ]


  SESSION_CONFIGS = [
    {
        'name': 'Tullock_Income_RET',
        'display_name': "Income Inequality and Human Capital",
        'num_demo_participants': 3,
        'app_sequence': ['Tullock_Income_RET'],
    },
    # other session configs go here ...
  ]
~~~
4. Either download or, ideally, clone this repository and add its contents to the "Tullock_Income_RET" folder.
1. This app runs on oTree 2.0, uses Bootstrap 4.0 and requires Python 3.6
1. This app is optimized for Chrome.
1. Ready! :-)

--


Note: This app was originally design for oTree 1.0 and was updated to 2.0 in May 2018. Some compatibility issues might
 still appear.
