import py4j.GatewayServer;

public class App {
    public static void main(String[] args) throws Exception {
        System.out.println("Hello, World!");
        GatewayServer gatewayServer = new GatewayServer(new App());
        gatewayServer.start();
        System.out.println("Gateway Server Started");
    }

    public int addition(int first, int second) {
        return first + second;
    }



}
