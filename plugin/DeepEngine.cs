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


        void Start()
        {
            Debug.Log("Kerbal DeepEngine Enabled");
            StartCoroutine(LoadFlightScene());
        }

        IEnumerator LoadFlightScene()
        {
            yield return new WaitForSeconds(1);
            Game game = GamePersistence.LoadGame("testergame", "default/", true, false);
            HighLogic.CurrentGame = game;
            //HighLogic.LoadScene(GameScenes.FLIGHT);
            game.startScene = GameScenes.FLIGHT;

            game.Start();
        }
    }

    [KSPAddon(KSPAddon.Startup.Flight, false)]
    public class FlightController : MonoBehaviour
    {
        private static readonly string fifoout = "/tmp/gamepipe.out";
        private static readonly string fifoin  = "/tmp/gamepipe.in";

        private Thread r_thread;
        private System.Object locking = new System.Object();
        private bool listening = false;
        private DeepEngineMessage inputmessage;
        private FlightCtrlState flightCtrl;

        void Start()
        {
            Debug.Log("Kerbal DeepEngine Flight Loaded");
            flightCtrl = new FlightCtrlState();

            Vessel vessel = FlightGlobals.ActiveVessel;
            vessel.OnFlyByWire = new FlightInputCallback(flightUpdate);
        }

        void GameStateListener(){
          try{
            FileStream infile = new FileInfo(fifoin).OpenRead();
            using (StreamReader reader = new StreamReader(infile, Encoding.UTF8))
            {
              string inmessage = reader.ReadLine();
              //Debug.Log("MESSAGE: " + inmessage);
              if(inmessage != null){
                 Debug.Log("DeepEngine: " + inmessage);
                 lock(locking){
                   try{
                     inputmessage = JsonUtility.FromJson<DeepEngineMessage>(inmessage);
                   }catch(Exception e){
                     Debug.Log(e.Source);
                   }
                 }
              }
            }
          } finally{
            listening = false;
          }
        }

        IEnumerator TransmitGameState()
        {
            yield return new WaitForEndOfFrame();

            try{
              DeepEngineMessage message = new DeepEngineMessage();
              message.vessel = JsonUtility.ToJson(FlightGlobals.ActiveVessel);
              message.flightCtrlState = JsonUtility.ToJson(flightCtrl);
              FileStream outfile = new FileInfo(fifoout).OpenWrite();
              using (StreamWriter writer  = new StreamWriter(outfile, Encoding.UTF8))
              {
                writer.WriteLine(JsonUtility.ToJson(message));
              }
            }catch(Exception e){
              Debug.Log(e.Source);
            }
        }

        void Update()
        {
          StartCoroutine(TransmitGameState());
          lock(locking){
            if(inputmessage != null){
              //Debug.Log("DeepEngine: " + inputmessage.flightCtrlState);
              if(inputmessage.action == DeepEngineMessage.FLIGHTCTRL)
              {
                  flightCtrl = JsonUtility.FromJson<FlightCtrlState>(inputmessage.flightCtrlState);
              }
              if(inputmessage.action == DeepEngineMessage.STAGING)
              {
                  KSP.UI.Screens.StageManager.ActivateNextStage();
              }
              if(inputmessage.action == DeepEngineMessage.RESETGAME)
              {
                  inputmessage = null;
                  FlightDriver.RevertToLaunch();
              }
              inputmessage = null;
            }
          }
          if(!listening){
            listening = true;
            Debug.Log("Start listening");
            r_thread = new Thread(GameStateListener);
            r_thread.Start();
          }
        }

        private void flightUpdate(FlightCtrlState flightCtrlState)
        {
            flightCtrlState.CopyFrom(flightCtrl);
        }
    }

    [System.Serializable]
    public class DeepEngineMessage
    {
        public static readonly int FLIGHTCTRL   = 0;
        public static readonly int STAGING      = 1;
        public static readonly int RESETGAME    = 2;
        public static readonly int LOADGAME     = 3;

        public string vessel;
        public string flightCtrlState;
        public int action = 0; /* Set Default Action To Flight Control */
        public string gamename;
        public long milliseconds = DateTime.Now.Ticks / TimeSpan.TicksPerMillisecond;
    }
}
