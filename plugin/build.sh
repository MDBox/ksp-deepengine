#!/bin/bash

bash -c "mcs DeepEngine.cs  /target:library -sdk:2 -r:../kerbal/KSP_linux/KSP_Data/Managed/UnityEngine.UI.dll  -r:../kerbal/KSP_linux/KSP_Data/Managed/Assembly-CSharp.dll -r:../kerbal/KSP_linux/KSP_Data/Managed/UnityEngine.dll -r:../kerbal/KSP_linux/KSP_Data/Managed/UnityEngine.Networking.dll"

cp ./DeepEngine.dll ../kerbal/KSP_linux/Plugins/
