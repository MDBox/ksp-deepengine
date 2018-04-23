using System;
using System.ComponentModel;
using System.Collections;
using System.Linq;
using System.Text;
using System.Net;  
using System.Net.Sockets;
using System.Threading;

using UnityEngine;
using UnityEngine.Networking;


namespace MDBox.KerbalDeepEngine
{    
    [KSPAddon(KSPAddon.Startup.MainMenu, false)]
    public class GameLoader: MonoBehaviour{
    
        public static Game game;
    
        void Start(){
            //game = GamePersistence.LoadGame("train1", "default/", true, false);
            //game.startScene = GameScenes.FLIGHT;
            //game.Start();            
        }
    }
    
    [KSPAddon(KSPAddon.Startup.Flight, false)]
    public class RemoteController : MonoBehaviour
    {
        private static FlightCtrlState flightCtrl = new FlightCtrlState();

        void Start(){

        }

        void Update()
        {
            //Vessel vessel = FlightGlobals.ActiveVessel;
            
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
        public static final int FLIGHTCTRL   = 0;
        public static final int STAGING      = 1;
        public static final int RESETGAME    = 2;
        public static final int LOADGAME     = 3;

        public Vessel vessel;
        public FlightCtrlState flightCtrlState;
        public int action;
        public string gamename;

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
}