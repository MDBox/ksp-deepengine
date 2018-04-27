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
            HighLogic.LoadScene(GameScenes.FLIGHT);
            game.Start();
        }
    }
    
    [KSPAddon(KSPAddon.Startup.Flight, false)]
    public class FlightController : MonoBehaviour
    {
        private static readonly string fifoout = "/tmp/gamepipe.out";
        private static readonly string fifoin  = "/tmp/gamepipe.in";


        private FlightCtrlState flightCtrl;

        //private DeepEngineIO networkPipe;

        void Start()
        {
            Debug.Log("Kerbal DeepEngine Flight Loaded");
            flightCtrl = new FlightCtrlState();
            //networkPipe = DeepEngineIO.getDefaultDeepEngineIO();

            Vessel vessel = FlightGlobals.ActiveVessel;
            vessel.OnFlyByWire = new FlightInputCallback(flightUpdate);
        }

        IEnumerator TransmitGameState()
        {
            yield return new WaitForFixedUpdate();
            DeepEngineMessage message = new DeepEngineMessage();
            message.vessel = JsonUtility.ToJson(FlightGlobals.ActiveVessel);
            message.flightCtrlState = JsonUtility.ToJson(flightCtrl);
            FileStream outfile = new FileInfo(fifoout).OpenWrite();
            StreamWriter writer  = new StreamWriter(outfile, Encoding.UTF8);
            writer.WriteLine(JsonUtility.ToJson(message));
            writer.Flush();
            writer.Close();
        }

        IEnumerator ReceiveGameState()
        {
            yield return new WaitForEndOfFrame();
            FileStream infile = new FileInfo(fifoin).OpenRead();
            StreamReader reader = new StreamReader(infile, Encoding.UTF8);
            string message = reader.ReadLine();
            if(message != null){
               DeepEngineMessage inputmessage = JsonUtility.FromJson<DeepEngineMessage>(message);
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
                   FlightDriver.RevertToLaunch();
               }
            }

        }

        void FixedUpdate()
        {
                    StartCoroutine(TransmitGameState());
        }


        void Update()
        {

            //StartCoroutine(ReceiveGameState());
        }

        private void flightUpdate(FlightCtrlState flightCtrlState)
        {
            flightCtrlState.CopyFrom(flightCtrl);
        }
    }

    [System.Serializable]
    public class DeepEngineMessage : System.Object
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



    public class DeepEngineIO{
        private static DeepEngineIO defaultDeepEngineIO;
        private static readonly string fifoout = "/tmp/gamepipe.out";
        private static readonly string fifoin  = "/tmp/gamepipe.in";

        private Queue inMessageQueue;
        private Queue outMessageQueue;

        public static DeepEngineIO getDefaultDeepEngineIO()
        {
            if(defaultDeepEngineIO == null)
            {
                defaultDeepEngineIO = new DeepEngineIO();
            }
            return defaultDeepEngineIO;
        }

        private DeepEngineIO()
        {
            inMessageQueue  = Queue.Synchronized(new Queue());
            outMessageQueue = Queue.Synchronized(new Queue());


            Thread inThread = new Thread(startInPipe);
            inThread.Start();

            Thread outThread = new Thread(startOutPipe);
            outThread.Start();
        }


        private void startOutPipe()
        {
            while(true)
            {
                if(outMessageQueue.Count > 0)
                {
                    FileStream outfile = new FileInfo(fifoout).OpenWrite();
                    StreamWriter writer  = new StreamWriter(outfile, Encoding.UTF8);
                    writer.WriteLine((string)outMessageQueue.Dequeue());
                    writer.Flush();
                    writer.Close();
                }
            }
        }

        private void startInPipe()
        {
            FileStream infile = new FileInfo(fifoin).OpenRead();
            StreamReader reader = new StreamReader(infile, Encoding.UTF8);

            while(true)
            {
                string message = reader.ReadLine();
                inMessageQueue.Enqueue(message);
            }
        }

        public void writeToOutPipe(string message)
        {
            outMessageQueue.Enqueue(message);
        }

        public string readFromInPipe()
        {
            if(inMessageQueue.Count > 0)
            {
                return (string)inMessageQueue.Dequeue();
            }else
            {
                return null;
            }
        }

    }
}