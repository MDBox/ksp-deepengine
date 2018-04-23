using System;
using System.Threading;
using System.IO;
using System.Text;
using System.Collections.Concurrent;

namespace MDBox.KerbalDeepEngine{

    class EngineIOPipe{

        static EngineIOPipe defaultEngineIOPipe;
        static string fifoout = "/tmp/gamepipe.out";
        static string fifoin = "/tmp/gamepipe.in";

        ConcurrentQueue<string> inMessageQueue;
        ConcurrentQueue<string> outMessageQueue;

        public static EngineIOPipe getDefaultEngineIOPipe(){
            if(defaultEngineIOPipe == null){
                defaultEngineIOPipe = new EngineIOPipe();
            }
            return defaultEngineIOPipe;
        }

        private EngineIOPipe(){
            inMessageQueue  = new ConcurrentQueue<string>();
            outMessageQueue = new ConcurrentQueue<string>();


            Thread inThread = new Thread(startInPipe);
            inThread.Start();

            Thread outThread = new Thread(startOutPipe);
            outThread.Start();
        }

        private void startOutPipe(){
            FileStream outfile = new FileInfo(fifoout).OpenWrite();
            StreamWriter writer  = new StreamWriter(outfile, Encoding.UTF8);

            while(true){
                string message;
                if(outMessageQueue.TryDequeue(out message)){
                    writer.Write(message);
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
            string message;
            if(inMessageQueue.TryDequeue(out message)){
                return message;
            }else{
                return null;
            }
        }
        
        static void Main(string[] args){
            new EngineIOPipe();
        }
    }
}