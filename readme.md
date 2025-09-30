# Bread Van CLI Application

This is a command-line interface for a bread van service, allowing drivers to manage their schedules and residents to view upcoming drives and make requests.

## Setup Instructions

Follow these steps to get the application running and populated with initial data.

### 1. Initialize the Database

This command will create and initialize the database tables.

```
$ flask init

database intialized
```

### 2. Create a Driver

Create at least one driver to manage schedules. The command prompts for a name and password.

```
$ flask driver create "Agnes the Breadwoman" "agnespass"

Driver: Agnes the Breadwoman created!
```

### 3. Create a Resident

Create residents who will interact with the drivers. The command prompts for a name, password, and street name.

```
$ flask resident create "Neil" "neilpass" "Main Street"

Resident: alice created!
```

## Usage

Once the application is set up with users, you can use the core commands, which are organized by user role.

### Driver Commands

These commands are used by a driver to manage their work.

**Schedule a Drive**

Schedules a new drive to a specific street at a given time. The command is interactive.

```
> flask driver schedule

--------- Select a Driver ---------
ID: 1 | Driver: Bob the Baker
ID: 2 | Driver: Alice the Patissier
ID: 3 | Driver: John the Breadman
-----------------------------------

Enter the ID of the driver to schedule: 1
Enter the street name: Elm Street
Enter the time (YYYY-MM-DD HH:MM): 2025-10-11 08:30
Success: Drive scheduled for Bob the Baker on Elm Street at 2025-10-11 08:30:00
```


**Update Status and Location**

Updates the driver's current status and location.

```
> flask driver update_status

--------- Select a Driver ---------
ID: 1 | Driver: Bob the Baker
ID: 2 | Driver: Alice the Patissier
ID: 3 | Driver: John the Breadman
-----------------------------------

Enter the ID of the driver to update: 1
Enter the new status: On Route
Enter the new location: Near Park Avenue
Success: Bob the Baker's status updated to 'On Route' at 'Near Park Avenue'.
```


**View Stop Requests**

Views all pending stop requests for a specific driver.

```
> flask driver view_requests

--------- Select a Driver ---------
ID: 1 | Driver: Bob the Baker
ID: 2 | Driver: Alice the Patissier
ID: 3 | Driver: John the Breadman
-----------------------------------

Enter the ID of the driver to view stop requests: 1
----------------------------------------------------- Stop Requests -----------------------------------------------------
Drive ID: 1 | Time: 2025-09-29 05:48 PM | Resident: Charlie | Message: Please stop near the grey house with the red door.
-------------------------------------------------------------------------------------------------------------------------
```

### Resident Commands

These commands are used by residents to interact with the service.

**View Inbox**

Views all upcoming drives scheduled for the resident's street.
Inbox with a drive:

```
> flask resident inbox

------------- Available Residents -------------
ID: 4 | Username: Charlie | Street: Main Street
ID: 5 | Username: Diana | Street: Park Avenue
ID: 6 | Username: Emily | Street: Elm Street
ID: 7 | Username: Frank | Street: Oak Road
-----------------------------------------------

Enter the ID of the resident to view their inbox: 6

----------------------------- Resident Inbox -----------------------------
Drive ID: 3 | Driver: John the Breadman | Scheduled Time: 2025-09-30 01:03
--------------------------------------------------------------------------
```


**Request a Stop**

Sends a stop request to a driver for a specific drive.
Drives available:

```
> resident request_stop

-------------- Select a Resident --------------
ID: 4 | Resident: Charlie | Street: Main Street
ID: 5 | Resident: Diana | Street: Park Avenue
ID: 6 | Resident: Emily | Street: Elm Street
ID: 7 | Resident: Frank | Street: Oak Road
-----------------------------------------------

Enter the ID of the resident making the request: 2

------------------------- Select a Drive to Stop -------------------------
Drive ID: 3 | Driver: John the Breadman | Scheduled Time: 2025-09-30 01:03
Drive ID: 5 | Driver: Bob the Baker | Scheduled Time: 2025-10-11 08:30
--------------------------------------------------------------------------

Enter the ID of the drive to stop: 5
Enter a message for the request: Hi, can you stop near the brick house with the grey roof? I'll wait outside.
Success: Stop request sent to driver Bob the Baker for drive on 2025-10-11 08:30
```


**Check Driver Status**

Gets the real-time status and location of a specific driver.

```
$ flask resident get_driver_status_and_location

----- Select a Driver to Check ----
ID: 1 | Driver: Bob the Baker
ID: 2 | Driver: Alice the Patissier
ID: 3 | Driver: John the Breadman
-----------------------------------

Enter the ID of the driver to check status: 1

---------------- Driver Status -----------------
Driver: Bob the Baker | Status: On Route | Current Location: Near Park Avenue
----------------------------------------------
```