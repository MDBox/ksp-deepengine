#!/bin/bash

bash -c "mcs deepengine.cs  /target:library -r:../kerbal/KSP_linux/KSP_Data/Managed/UnityEngine.UI.dll  -r:../kerbal/KSP_linux/KSP_Data/Managed/Assembly-CSharp.dll -r:../kerbal/KSP_linux/KSP_Data/Managed/UnityEngine.dll -r:../kerbal/KSP_linux/KSP_Data/Managed/UnityEngine.Networking.dll"

cp ./deepengine.dll ../kerbal/KSP_linux/Plugins/
