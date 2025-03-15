import java.io.*;
import java.util.*;

public class OS1Assignment {
    static final HashMap<Integer, Integer> table = new HashMap<>();
    static final int offset = 5;
    public static void main (String[] args) {
        // insert pages into the page table
        table.put(0, 2);
        table.put(1, 4);
        table.put(2, 1);
        table.put(3, 7);
        table.put(4, 3);
        table.put(5, 5);
        table.put(6, 6);

        // prompt user to enter file as command line input
        if(args.length!=1){
            System.out.println("Program takes one input parameter <filename>.");
            System.out.println("Terminating program.");
            System.exit(0);
        }
        else{
            // read in hexadec and convert to string
            try (DataInputStream line = new DataInputStream(new FileInputStream(args[0]))) {
                // prepare a new file for output
                FileWriter output = new FileWriter("output-OS1");
                // sets buffer size to 8
                byte[] buffer = new byte[Byte.SIZE];
                System.out.println("File read in successfully.\nSetting page table.\nTranslating virtual addresses to physical addresses.");
                // converts virtual mem address table to a physical address table
                HashMap<Integer, String> physicalTable = OS1Assignment.physicalTable(table);
                // translate while there are lines in the file
                while (line.read(buffer) != -1) {                   
                    long b = 0;                                     
                    for (int i = 0; i < buffer.length; i++) {                   // reads in the bytes from the byte array
                        b += ((long) buffer[i] & 0xFF) * Math.pow(2, 8 * i);  // converts byte to long, take only the 8 least significant bits, shift to correct position
                    }
                    // convert the byte to binary
                    String binary = OS1Assignment.finBinary(byteToBinary(b), 12);   
                    // get the page number needed
                    String pageNum = binary.substring(0, 5);        
                    // get binary rep of page num from hashmap & concat page entry with page offset
                    binary = physicalTable.get((int) Long.parseLong(pageNum, 2)) + binary.substring(5, binary.length());
                    // write the outputs to the output file
                    output.write(OS1Assignment.outputFormat(Long.toHexString(Long.parseLong(binary, 2))) + "\n");
                }
                output.close();
                System.out.println("Physical addresses written to output file \"output-OS1\".");
            } catch(IOException e) {
                System.out.println("File not found.");
            } 
        }   
    }

    // convert from virtual mem table to physical mem table
    private static HashMap<Integer, String> physicalTable(HashMap<Integer, Integer> table){
        HashMap<Integer, String> physicalTable = new HashMap<>(table.size());                               // sets hashmap to be same size as the original
        for (Integer pageNumber : table.keySet()) {                                                         // goes through each key in the VM table
            Integer entry = table.get(pageNumber);                                                          // get retrieves page entry related to page number
            physicalTable.put(pageNumber, OS1Assignment.finBinary(Integer.toBinaryString(entry), offset));  // put entry into physical hashmap
        }
        return physicalTable;
    }

    // convert bytes to binary
    private static String byteToBinary(long b) {
        return String.format("%8s", Long.toBinaryString(b)).replace(" ", "0");    // format the binary string to be 8 bits long with empty spaces replaced with 0
    }

    // format binary to particular length
    private static String finBinary(String in,int len){
        int max = len - in.length();
        for(int i = 0; i < max; i++){
            in = "0" + in;
        }
        return in;
    }

    // format to output in form of 0x...
    private static String outputFormat(String in) {
        int max = 7 - (in.length()/2 + in.length()%2);
        for(int i = 0; i < max; i++) {
            in = "0" + in;                              // get it to the correct length
        }
        return "0x" + in.toUpperCase();                 // 0x the string
    }
}
