using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;

using System.ServiceModel.Channels;
using System.ServiceModel.Dispatcher;
using System.ServiceModel.Description;
using System.ServiceModel;
using System.Xml;
using System.Diagnostics;

public class MessageInspector : IClientMessageInspector
{
    public void AfterReceiveReply(ref System.ServiceModel.Channels.Message reply, object correlationState) { }

    public object BeforeSendRequest(ref System.ServiceModel.Channels.Message request, IClientChannel channel)
    {
        Debug.WriteLine(request.ToString());
        return null;
    }
}

public class EndpointBehavior : IEndpointBehavior
{
    public void AddBindingParameters(ServiceEndpoint endpoint, BindingParameterCollection bindingParameters) { }

    public void ApplyClientBehavior(ServiceEndpoint endpoint, ClientRuntime clientRuntime)
    {
        clientRuntime.ClientMessageInspectors.Add(new MessageInspector());
    }

    public void ApplyDispatchBehavior(ServiceEndpoint endpoint, EndpointDispatcher endpointDispatcher) { }

    public void Validate(ServiceEndpoint endpoint) { }
}


namespace DbmsSoapClient
{
    internal static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            var result = FormStartDialog.ShowStartDialog();
            if (!result.HasValue)
                return;
            try
            {
                var client = new DbmsSoapServiceReference.ApplicationClient();
                client.Endpoint.EndpointBehaviors.Add(new EndpointBehavior());
                switch (result.Value.action)
                {
                    case FormStartDialog.Action.CREATE:
                        client.CreateDatabase(new() { DbName = result.Value.text });
                        break;
                    case FormStartDialog.Action.OPEN:
                        break;
                    case FormStartDialog.Action.DELETE:
                        client.DeleteDatabase(new() { DbName = result.Value.text });
                        return;
                }
                Application.Run(new FormDatabase(client, result.Value.text));
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
