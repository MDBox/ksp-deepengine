using System;
using System.Runtime.Serialization;
using System.ComponentModel;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;  
using System.Net.Sockets;
using System.Threading;
using System.IO;

using UnityEngine;
using UnityEngine.Networking;

namespace MDBox
{    
    [KSPAddon(KSPAddon.Startup.MainMenu, false)]
    public class GameLoader: MonoBehaviour{
    

    
        void Start(){
            Debug.Log("Kerbal DeepEngine Enabled");
            Game game = GamePersistence.LoadGame("testergame", "default/", true, false);
            if(game == null){
                Debug.Log("DeepEngine Game is Null");
            }else{
               Debug.Log("DeepEngine Game is loaded");
               game.startScene = GameScenes.;

               //game.Load();
               //HighLogic.LoadScene(GameScenes.FLIGHT);
               game.Start();
            }
        }

        void Update(){
        }
    }
    
    [KSPAddon(KSPAddon.Startup.Flight, false)]
    public class RemoteController : MonoBehaviour
    {

        private static FlightCtrlState flightCtrl = new FlightCtrlState();

        private DeepEngineIO networkPipe = DeepEngineIO.getDefaultDeepEngineIO();

        void Start(){
            Debug.Log("Kerbal DeepEngine Flight Loaded");


        }

        void Update()
        {
            Vessel vessel = FlightGlobals.ActiveVessel;
            DeepEngineMessage message = new DeepEngineMessage();
            message.vessel = vessel;
            message.flightCtrlState = flightCtrl;
            //networkPipe.writeToOutPipe(JsonUtility.ToJson(message));
            //Debug.Log(JsonUtility.ToJson(vessel));
            //string netmessage = networkPipe.readFromInPipe();
            //if(netmessage != null){
            //    print(netmessage);
            //}
            
            //if(firstAction){
            //    Invoke("onDeath", 30);
            //}
            
            //if(vessel.altitude < 5){
            //    onDeath();
            //}else if(input.Count > 0){
            //    ActionJSON a = JsonUtility.FromJson<ActionJSON>((string)input.Dequeue());
            //    updateFlightCtrl(a.action);
            //    Invoke("updateNetwork", (float)a.delayms/1000);  
            //}
        }
        
        private void onDeath(){
        }
        
        private void onCrash(EventReport report){
        }
        
        private void flightReady(){
            //firstAction = true;
            //KSP.UI.Screens.StageManager.ActivateNextStage();
        }
        
        private void reset(){
            //CancelInvoke();
            //FlightDriver.RevertToLaunch();
            //Game game = GamePersistence.LoadGame("train1", "default/", true, false);
            //game.startScene = GameScenes.MAINMENU;
            //game.Start();            
            
            //flightCtrl = new FlightCtrlState();
            //Vessel vessel = FlightGlobals.ActiveVessel;
            //vessel.OnFlyByWire = new FlightInputCallback(flightUpdate);
            //InvokeRepeating("updateNetwork", 0, 1.0f);            
        }
        
        private void flightUpdate(FlightCtrlState st){
            //st.CopyFrom(flightCtrl);
        }

    }

    [Serializable]
    public class DeepEngineMessage : ISerializable
    {
        public static readonly int FLIGHTCTRL   = 0;
        public static readonly int STAGING      = 1;
        public static readonly int RESETGAME    = 2;
        public static readonly int LOADGAME     = 3;

        public Vessel vessel;
        public FlightCtrlState flightCtrlState;
        public int action;
        public string gamename;

        public DeepEngineMessage(){
        }

        public void GetObjectData(SerializationInfo info, StreamingContext context)
        {
            info.AddValue("vessel", vessel, typeof(Vessel));
            info.AddValue("flightCtrlState", flightCtrlState, typeof(FlightCtrlState));
            info.AddValue("action", action, typeof(int));
            info.AddValue("gamename", gamename, typeof(string));
        }

        public DeepEngineMessage(SerializationInfo info, StreamingContext context)
        {
            vessel = (Vessel) info.GetValue("vessel", typeof(Vessel));
            flightCtrlState = (FlightCtrlState) info.GetValue("flightCtrlState", typeof(FlightCtrlState));
            action = (int) info.GetValue("action", typeof(int));
            gamename = (string) info.GetValue("gamename", typeof(string));
        }
    }

    public class DeepEngineIO{
        private static DeepEngineIO defaultDeepEngineIO;
        private static readonly string fifoout = "/tmp/gamepipe.out";
        private static readonly string fifoin  = "/tmp/gamepipe.in";

        private Queue<string> inMessageQueue;
        private Queue<string> outMessageQueue;

        public static DeepEngineIO getDefaultDeepEngineIO(){
            if(defaultDeepEngineIO == null){
                defaultDeepEngineIO = new DeepEngineIO();
            }
            return defaultDeepEngineIO;
        }

        private DeepEngineIO(){
            inMessageQueue  = new Queue<string>();
            outMessageQueue = new Queue<string>();


            Thread inThread = new Thread(startInPipe);
            inThread.Start();

            Thread outThread = new Thread(startOutPipe);
            outThread.Start();
        }


        private void startOutPipe(){
            FileStream outfile = new FileInfo(fifoout).OpenWrite();
            StreamWriter writer  = new StreamWriter(outfile, Encoding.UTF8);

            while(true){
                if(outMessageQueue.Count > 0){
                    writer.Write(outMessageQueue.Dequeue());
                    writer.Flush();
                }
            }
        }

        private void startInPipe(){
            FileStream infile = new FileInfo(fifoin).OpenRead();
            StreamReader reader = new StreamReader(infile, Encoding.UTF8);

            while(true){
                string message = reader.ReadLine();
                inMessageQueue.Enqueue(message);
            }
        }

        public void writeToOutPipe(string message){
            outMessageQueue.Enqueue(message);
        }

        public string readFromInPipe(){
            if(inMessageQueue.Count > 0){
                return inMessageQueue.Dequeue();
            }else{
                return null;
            }
        }

    }
}