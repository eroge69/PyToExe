using System;
using DiscordRPC;

namespace SoulDiscordStatus
{
    class Program
    {
        static DiscordRpcClient client;

        static void Banner()
        {
            Console.WriteLine("========================================");
            Console.WriteLine("                 SOUL                   ");
            Console.WriteLine("========================================");
        }

        static void Menu()
        {
            Console.WriteLine("1. Set Status");
            Console.WriteLine("2. Clear Status");
            Console.WriteLine("3. Exit");
        }

        static void Main(string[] args)
        {
            Console.Title = "SOUL Discord Status Changer";
            Banner();
            Console.Write("Enter your Discord Discord Token: ");
            string clientId = Console.ReadLine();

            client = new DiscordRpcClient(clientId);

            try
            {
                client.Initialize();
            }
            catch
            {
                Console.WriteLine("Could not connect to Discord. Make sure Discord is running.");
                Console.ReadKey();
                return;
            }

            while (true)
            {
                Console.Clear();
                Banner();
                Menu();
                Console.Write("Choose an option: ");
                string choice = Console.ReadLine();

                if (choice == "1")
                {
                    Console.Write("Enter your status message: ");
                    string state = Console.ReadLine();
                    Console.Write("Enter details (optional): ");
                    string details = Console.ReadLine();

                    client.SetPresence(new RichPresence()
                    {
                        State = state,
                        Details = details
                    });

                    Console.WriteLine("Status updated! Press Enter to continue...");
                    Console.ReadLine();
                }
                else if (choice == "2")
                {
                    client.ClearPresence();
                    Console.WriteLine("Status cleared! Press Enter to continue...");
                    Console.ReadLine();
                }
                else if (choice == "3")
                {
                    client.ClearPresence();
                    client.Dispose();
                    Console.WriteLine("Goodbye!");
                    break;
                }
                else
                {
                    Console.WriteLine("Invalid choice. Press Enter to try again...");
                    Console.ReadLine();
                }
            }
        }
    }
}