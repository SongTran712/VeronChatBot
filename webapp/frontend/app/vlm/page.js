"use client";
import Image from "next/image";
import { useState, useEffect } from "react";
// import Markdown from "marked-react";
// import Markdown from 'markdown-to-jsx'
// import { render } from 'react-dom'
import ReactMarkdown from 'react-markdown'
import { marked } from 'marked';
import { v4 as uuidv4 } from 'uuid';
// import { ChevronLeft, ChevronRight } from 'lucide-react'
import { FaSearch } from 'react-icons/fa';
import { FaChevronLeft, FaChevronRight } from "react-icons/fa";
import { useRouter } from 'next/navigation'
import { Upload, User } from 'lucide-react';

export default function Home() {
  const router = useRouter()
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [inputColor, setInputColor] = useState('black')
  const [loading, setLoading] = useState(false);
  const [sessionID, setSessionID] = useState(null);
  const [showSidebar, setShowSidebar] = useState(true)
  const [collapsed, setCollapsed] = useState(false);
  const [selectedField, setSelectedField] = useState('');
  const [textValue, setTextValue] = useState('');
  const [file, setFile] = useState(null);

const ChatItem = ({ imgSrc, name, lastMsg, route }) => (
  <div
    className="flex flex-row py-4 px-2 items-center border-b hover:bg-gray-100 transition cursor-pointer"
    onClick={() => router.push(route)}
  >
    <div className="w-1/4">
      <img src={imgSrc} alt={name} className="object-cover h-12 w-12 rounded-full" />
    </div>
    <div className="w-full">
      <div className="text-md text-black font-semibold">{name}</div>
      <span className="text-gray-500 text-sm truncate">{lastMsg}</span>
    </div>
  </div>
);

 const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files.length) {
      setFile(e.dataTransfer.files[0]);
    }
  };
  const chatList = [
    { imgSrc: '/agent.avif', name: 'Agent', lastMsg: 'Last message preview', route: '/' },
    { imgSrc: '/vlm.jpg', name: 'VLMs', lastMsg: 'Last message preview', route:'/vlm' },
  ]

  useEffect(() => {
    // If the messages array is empty, create a sessionID
    if (messages.length === 0 && !sessionID) {
      const generatedSessionID = uuidv4(); // Generate a random UUID
      setSessionID(generatedSessionID);
    }
  }, [messages, sessionID]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
    setInputColor('black');
  };

  const sendMessage = async () => {
    if (!input.trim()) return; // If input is empty, do nothing.
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]); // Add user message to chat
    setInput(""); // Clear the input
    setLoading(true); // Start loading indicator
    
    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: input, user:"testuser", sessionID: sessionID }),
      });
  
      if (!response.ok) {
        throw new Error('Failed to fetch response from the server');
      }
  
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
  
      let botMessage = { role: "assistant", content: "" }; // Initial empty AI message
      setMessages((prev) => [...prev, botMessage]); // Add empty message to array
  
      const readStream = async () => {
        const { value, done } = await reader.read();
        if (done) {
          setLoading(false); // Stop loading once the stream is finished
          return;
        }
  
        let token = decoder.decode(value, { stream: true }); // Decode the chunk of data
  
        setMessages((prev) => {
          let updatedMessages = [...prev];
          updatedMessages[updatedMessages.length - 1] = {
            role: "assistant",
            content: updatedMessages[updatedMessages.length - 1].content + token, // Append token
          };
          return updatedMessages;
        });
  
        // Recursively call readStream to continue reading
        if (!done) {
          readStream();
        }
      };
  
      // Start reading the stream
      readStream();
  
    } catch (error) {
      console.error("Error occurred while sending the message:", error);
      setLoading(false); // Ensure loading stops if there is an error
      // Optionally show an error message to the user
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, something went wrong!" }]);
    }
  };
  


  return (
    <div className="flex flex-col min-h-screen">
      <header style={{ backgroundColor: "#17407B" }} className="text-white py-6 px-8 shadow-md relative flex items-center">
        {/* Logo */}
        <div className="flex items-center gap-4">
          <Image src="/veron-logo-rm.png" alt="Veron Logo" width={160} height={40} />
        </div>

        {/* Centered Title */}
        <div className="absolute left-1/2 transform -translate-x-1/2 text-3xl font-bold tracking-wide flex items-center gap-4">
          <h1>VERON Chatbot</h1> {/* Added margin-right to separate text from image */}
          <Image src="/robo.png" alt="Veron Logo" width={80} height={10} />
        </div>

        {/* Right Label */}
        <span className="ml-auto text-gray-300 text-sm">Powered by VERON R&D</span>
      </header>

      <main className="flex-1 w-full h-screen flex flex-col gap-8 row-start-2">
       
      
<div className="w-full flex flex-col h-[90vh]">
    <div className="flex flex-row justify-between bg-white h-full">
      <div className={`flex flex-col ${collapsed ? 'w-16' : 'w-1/5'} border-r-2 overflow-y-auto transition-all duration-300`}>
    <div className="flex  justify-between border-b-2  py-4 px-2">
          
    {!collapsed && (

            <div>
              
            <div className="">
              <div className="flex items-center border-2 border-gray-200 rounded-2xl px-2">
                <input
                  type="text"
                  placeholder="Search chatting"
                  className="py-2 px-2 w-full focus:outline-none rounded-2xl"
                />
                <FaSearch className="text-gray-500 h-4 w-4 ml-2" />
              </div>
            </div>

            </div>
          )}
                {/* Collapse/Expand Button */}
                <div className="flex justify-end p-2">
            <button onClick={() => setCollapsed(!collapsed)}>
              {collapsed ? (
                <FaChevronRight className="text-gray-600" />
              ) : (
                <FaChevronLeft className="text-gray-600" />
              )}
            </button>
          </div>

    </div>


          {/* Search Input */}
          {!collapsed && (
            <div>


           {chatList.map((chat, idx) => (
              <ChatItem key={idx} {...chat} />
            ))}
            </div>
          )}
  
      </div>


      

      
      <div className="relative w-full px-5 flex flex-col justify-between bg-cover bg-center overflow-hidden"  >

          


        <div className="flex flex-col mt-5" >
        

<div className="w-full max-w-md p-6 bg-white rounded-2xl shadow-xl space-y-6">
        
        {/* Hello User */}
        {/* <div className="flex items-center space-x-3"> */}
          <User className="text-blue-500" />
          <h1 className="text-xl font-semibold text-gray-800">Hello, User</h1>
        {/* </div> */}

        {/* Select Field */}
        <div>
          <label className="block text-gray-700 font-medium mb-2">Please select a field:</label>
          <select
            value={selectedField}
            onChange={(e) => setSelectedField(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Select --</option>
            <option value="text">Text</option>
            <option value="file">File</option>
          </select>
        </div>

        {/* Input Field */}
        <div className="space-y-2">
          <label className="block text-gray-700 font-medium">Enter text or drop a file below:</label>

          {selectedField === 'text' && (
            <input
              type="text"
              placeholder="Enter text..."
              value={textValue}
              onChange={(e) => setTextValue(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-lg"
            />
          )}

          {selectedField === 'file' && (
            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              className="w-full p-4 text-center border-2 border-dashed border-gray-400 rounded-lg text-gray-500 cursor-pointer"
            >
              <Upload className="mx-auto mb-2" />
              {file ? file.name : 'Drop file here or click to upload'}
              <input
                type="file"
                onChange={(e) => e.target.files && setFile(e.target.files[0])}
                className="hidden"
              />
            </div>
          )}
        </div>
      </div>


  
</div>
      </div>
      
      
      </div>
</div>

      </main>
    </div>
  );
}
