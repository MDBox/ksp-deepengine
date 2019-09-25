using System;
using System.Collections;
using System.Text;
using System.Threading;
using System.IO;
using UnityEngine;

namespace DeepSpaceEngine
{

    [KSPAddon(KSPAddon.Startup.MainMenu, false)]
    public class GameLoader: MonoBehaviour
    {

        public static string GAMEPATH = "../Plugins/deep_engine/challenge1/";
        
        void Start()
        {
            Debug.Log("Kerbal DeepEngine Enabled");
            StartCoroutine(LoadFlightScene());
        }

        IEnumerator LoadFlightScene()
        {
            yield return new WaitForSeconds(1);
            Game game = GamePersistence.LoadGame("quicksave", GAMEPATH, true, false);
            HighLogic.CurrentGame = game;
            //HighLogic.LoadScene(GameScenes.FLIGHT);
            game.startScene = GameScenes.FLIGHT;

            game.Start();
        }
    }
    
    [KSPAddon(KSPAddon.Startup.Flight, false)]
    public class DeepEngine : MonoBehaviour
    {
        private static readonly string fifoout = "/tmp/gamepipe.out";
        private static readonly string fifoin  = "/tmp/gamepipe.in";

        private Thread read_thread;
        private System.Object locking = new System.Object();
        private DeepEngineMessage inputmessage = null;
        private bool listening = false;
        private bool crashed = false;
        private FlightCtrlState flightCtrl;
        
        void Start()
        {
            Debug.Log("Kerbal DeepEngine Flight Loaded");
            flightCtrl = new FlightCtrlState();

            Vessel vessel = FlightGlobals.ActiveVessel;
            vessel.OnFlyByWire = new FlightInputCallback(flightUpdate);
            vessel.OnJustAboutToBeDestroyed = new Callback(OnCrash);
        }
        
        private void flightUpdate(FlightCtrlState flightCtrlState)
        {
            flightCtrlState.CopyFrom(flightCtrl);
        }

        private void OnCrash()
        {
            Debug.Log("Crash Detected");
            crashed = true;
        }
        
        void GameStateListener(){
            try{
                FileStream infile = new FileInfo(fifoin).OpenRead();
                using (StreamReader reader = new StreamReader(infile, Encoding.UTF8))
                {
                    string inmessage = reader.ReadLine();
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
                Debug.Log("End Read Listener");
                listening = false;
            }
        }

        void StartGameListener()
        {
            if (!listening && inputmessage == null)
            {
                listening = true;
                Debug.Log("Start listening");
                read_thread = new Thread(GameStateListener);
                read_thread.Start();                
            }
        }
        
        IEnumerator TransmitGameState()
        {
            yield return new WaitForEndOfFrame();

            try
            {
                DeepEngineMessage message = new DeepEngineMessage();
                message.vessel = JsonUtility.ToJson(FlightGlobals.ActiveVessel);
                message.gamepath = GameLoader.GAMEPATH;
                message.flightCtrlState = JsonUtility.ToJson(flightCtrl);
                if (crashed)
                {
                    message.action = DeepEngineMessage.CRASHED;
                }

                FileStream outfile = new FileInfo(fifoout).OpenWrite();
                using (StreamWriter writer = new StreamWriter(outfile, Encoding.UTF8))
                {
                    writer.WriteLine(JsonUtility.ToJson(message));
                }
            }
            catch (Exception e)
            {
                Debug.Log(e.Source);
            }
            finally
            {
                Debug.Log("Transmit finished");
                inputmessage = null;
            }
        }
        
        void Update()
        {
            
            lock(locking){
                if(inputmessage != null){
                    if(inputmessage.action == DeepEngineMessage.FLIGHTCTRL)
                    {
                        flightCtrl = JsonUtility.FromJson<FlightCtrlState>(inputmessage.flightCtrlState);
                    }
                    if(inputmessage.action == DeepEngineMessage.STAGING)
                    {
                        KSP.UI.Screens.StageManager.ActivateNextStage();
                    }
                    if (inputmessage.action == DeepEngineMessage.STATEONLY)
                    {
                        // Just Return State
                    }

                    if (inputmessage.action == DeepEngineMessage.LOADGAME && inputmessage.gamepath != null)
                    {
                        Debug.Log("Load Game: " + inputmessage.gamepath);
                        read_thread.Abort();
                        crashed = false;
                        GameLoader.GAMEPATH = inputmessage.gamepath;
                        HighLogic.CurrentGame.startScene = GameScenes.MAINMENU;
                        HighLogic.CurrentGame.Start();
                    }
                    
                    if(inputmessage.action == DeepEngineMessage.RESETGAME)
                    {
                        read_thread.Abort();
                        crashed = false;
                        FlightDriver.RevertToLaunch();
                    }
                    StartCoroutine(TransmitGameState());
                }
            }
            if(!listening && inputmessage == null){
                StartGameListener();
            }
        }

    }
    
    [System.Serializable]
    public class DeepEngineMessage
    {
        public static readonly int FLIGHTCTRL   = 0;
        public static readonly int STAGING      = 1;
        public static readonly int RESETGAME    = 2;
        public static readonly int CRASHED      = 3;
        public static readonly int STATEONLY    = 4;
        public static readonly int LOADGAME     = 5;

        public string gamepath;
        public string vessel;
        public string flightCtrlState;
        public int action = 0; /* Set Default Action To Flight Control */
    }
}