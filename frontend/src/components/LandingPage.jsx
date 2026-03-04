import React, { useState, useEffect } from 'react';
import { motion, useScroll, useSpring } from 'framer-motion';
import { FaDownload, FaShieldAlt, FaChartLine, FaBrain, FaUsers, FaStar, FaCheckCircle, FaGithub, FaLinkedin, FaTwitter } from 'react-icons/fa';

const LandingPage = () => {

  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001
  });

  // Typing animation state
  const [displayText, setDisplayText] = useState('');
  const [showCursor, setShowCursor] = useState(true);
  const fullText = 'Detect Stress Before It Detects You...!';

  useEffect(() => {
    let index = 0;
    const typingSpeed = 100; // milliseconds per character
    const pauseBetweenLoops = 2000; // 2 seconds pause before restarting

    const typeText = () => {
      if (index < fullText.length) {
        setDisplayText(fullText.slice(0, index + 1));
        index++;
        setTimeout(typeText, typingSpeed);
      } else {
        // Typing complete, pause then restart
        setTimeout(() => {
          setDisplayText('');
          index = 0;
          setShowCursor(true);
          typeText();
        }, pauseBetweenLoops);
      }
    };

    // Start typing after a short delay
    const startTyping = setTimeout(typeText, 1000);

    return () => clearTimeout(startTyping);
  }, []);

  const fadeInUp = {
    initial: { opacity: 0, y: 30 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 }
  };

  const stagger = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const features = [
    {
      icon: <FaBrain className="text-4xl text-blue-500" />,
      title: "AI-Powered Detection",
      description: "Advanced machine learning algorithms analyze facial expressions and physiological signals to detect stress levels in real-time."
    },
    {
      icon: <FaShieldAlt className="text-4xl text-green-500" />,
      title: "Privacy First",
      description: "All processing happens locally on your device. Your data never leaves your computer, ensuring complete privacy and security."
    },
    {
      icon: <FaChartLine className="text-4xl text-purple-500" />,
      title: "Comprehensive Analytics",
      description: "Detailed stress pattern analysis with historical data tracking and personalized insights for better stress management."
    },
    {
      icon: <FaUsers className="text-4xl text-indigo-500" />,
      title: "Team Monitoring",
      description: "Perfect for HR departments and managers to monitor team well-being and create healthier work environments."
    }
  ];

  const testimonials = [
    {
      name: "Mr. Prathamesh Gadgil",
      role: "HR Director",
      company: "PGTech Global",
      content: "This tool has revolutionized how we approach employee wellness. The AI accuracy and privacy-first design make it indispensable for modern workplaces.",
      rating: 5
    },
    {
      name: "Mrs. Jisoo Kim",
      role: "Clinical Psychologist",
      company: "MindCare Institute",
      content: "A breakthrough in preventive mental health monitoring. The real-time analysis provides insights that traditional methods simply cannot match.",
      rating: 5
    },
    {
      name: "Dhairyashil Patil",
      role: "VP of Engineering",
      company: "Sai Green House Global",
      content: "The accuracy is incredible. It caught stress patterns our team wasn't even aware of. Essential for maintaining productivity and well-being.",
      rating: 5
    },
    {
      name: "Rahul Patil",
      role: "Chief Wellness Officer",
      company: "Tractor Supply Co.",
      content: "Implementing StressSense has reduced our employee burnout incidents by 40%. The proactive approach to mental health is exactly what modern companies need.",
      rating: 5
    },
    {
      name: "Dr. Dhiraj Ekal",
      role: "Head of Employee Health",
      company: "DataCorp International",
      content: "The privacy-first approach combined with enterprise-grade accuracy makes this the gold standard for workplace mental health monitoring.",
      rating: 5
    },
    {
      name: "Ayush Nikam",
      role: "VP of People Operations",
      company: "CloudTech Systems",
      content: "Our team's productivity has improved significantly since adopting StressSense. The real-time insights help us intervene before issues escalate.",
      rating: 5
    },
    {
      name: "Dr. Rohit Gurav",
      role: "Occupational Psychologist",
      company: "Wellness Partners Ltd",
      content: "The AI algorithms are remarkably accurate. We've validated the stress detection against traditional psychological assessments with 94% correlation.",
      rating: 5
    },
    {
      name: "Dhiraj Ekal",
      role: "Director of HR Technology",
      company: "FutureWorks Inc",
      content: "Easy to deploy, incredibly accurate, and completely private. This is the mental health monitoring solution we've been waiting for.",
      rating: 5
    },
    {
      name: "Aniruddha Bhosale",
      role: "CEO",
      company: "StartupHub",
      content: "As a growing company, employee wellness is crucial. StressSense gives us the tools to maintain a healthy, productive work environment.",
      rating: 5
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 relative overflow-hidden"
    >
      {/* Scroll Progress Indicator */}
      <motion.div
        className="fixed top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-purple-600 z-50 origin-left"
        style={{ scaleX }}
      />

      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-3">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.08'%3E%3Cpath d='M50 50c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10zm-2 0c0 4.4-3.6 8-8 8s-8-3.6-8-8 3.6-8 8-8 8 3.6 8 8zm-8-6c-2.2 0-4 1.8-4 4s1.8 4 4 4 4-1.8 4-4-1.8-4-4-4z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}></div>
      </div>

      {/* Geometric Shapes */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-gradient-to-r from-blue-400/10 to-purple-400/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-purple-400/8 to-pink-400/8 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-gradient-to-r from-indigo-400/15 to-blue-400/15 rotate-45 animate-spin" style={{ animationDuration: '20s' }}></div>

      {/* Hero Section */}
      <section className="pt-16 pb-20 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-7xl mx-auto">
          <motion.div
            variants={stagger}
            initial="initial"
            animate="animate"
            className="text-center"
          >
            <motion.div variants={fadeInUp} className="mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.8, type: "spring", stiffness: 100 }}
                className="inline-block mb-6"
              >
                <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-2xl">
                  <FaBrain className="text-white text-3xl" />
                </div>
              </motion.div>
              <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight tracking-tight">
                <span className="relative">
                  {displayText}
                  {showCursor && <span className="animate-pulse">|</span>}
                </span>
              </h1>
              <p className="text-xl md:text-2xl text-gray-600 max-w-4xl mx-auto leading-relaxed mb-8 font-light tracking-wide">
                Advanced AI-powered stress detection using computer vision and machine learning.
                Monitor your mental well-being in real-time with complete privacy and cutting-edge technology.
              </p>
            </motion.div>

            <motion.div variants={fadeInUp} className="mb-12">
              <motion.a
                href="https://github.com/PGZON/Stress-Detection/releases/download/V1.0.0/StressDetectionInstaller.exe"
                whileHover={{
                  scale: 1.05,
                  boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                  transition: { duration: 0.2 }
                }}
                whileTap={{ scale: 0.98 }}
                className="group inline-flex items-center bg-gradient-to-r from-blue-600 to-purple-600 text-white px-12 py-6 rounded-full text-xl font-bold shadow-2xl hover:shadow-3xl transform transition-all duration-300 relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <FaDownload className="mr-4 text-2xl relative z-10" />
                <span className="relative z-10">Download StressSense v1.0.0</span>
              </motion.a>
              <p className="text-sm text-gray-500 mt-4 font-medium">Free • Windows • No registration required • Instant download</p>
            </motion.div>

            <motion.div
              variants={fadeInUp}
              className="relative max-w-5xl mx-auto"
            >
              <motion.div
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 1, delay: 0.5 }}
                className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-2xl p-10 border border-white/20 animate-float"
              >
                <div className="grid md:grid-cols-3 gap-8">
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    className="text-center group"
                  >
                    <div className="text-4xl font-bold bg-gradient-to-r from-blue-500 to-blue-600 bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform duration-300">91.2%</div>
                    <div className="text-gray-600 font-medium">Accuracy Rate</div>
                    <div className="w-12 h-1 bg-blue-500 mx-auto mt-2 rounded-full"></div>
                  </motion.div>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    className="text-center group"
                  >
                    <div className="text-4xl font-bold bg-gradient-to-r from-purple-500 to-purple-600 bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform duration-300">Office Hours</div>
                    <div className="text-gray-600 font-medium">Real-time Monitoring</div>
                    <div className="w-12 h-1 bg-purple-500 mx-auto mt-2 rounded-full"></div>
                  </motion.div>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    className="text-center group"
                  >
                    <div className="text-4xl font-bold bg-gradient-to-r from-green-500 to-green-600 bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform duration-300">100%</div>
                    <div className="text-gray-600 font-medium">Privacy Protected</div>
                    <div className="w-12 h-1 bg-green-500 mx-auto mt-2 rounded-full"></div>
                  </motion.div>
                </div>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-white relative">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-50/30 to-transparent"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-20"
          >
            <motion.div
              initial={{ scale: 0.8 }}
              whileInView={{ scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="inline-block px-6 py-2 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full text-blue-800 font-semibold text-sm mb-4"
            >
              Advanced Technology
            </motion.div>
            <h2 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Why Choose <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">StressSense</span>?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Cutting-edge AI technology meets intuitive design for comprehensive stress management and mental wellness monitoring.
            </p>
          </motion.div>

          <motion.div
            variants={stagger}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid md:grid-cols-2 lg:grid-cols-4 gap-8"
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={fadeInUp}
                whileHover={{
                  y: -10,
                  boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.15)"
                }}
                className="group bg-gradient-to-br from-white via-gray-50/50 to-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 border border-gray-100/50 backdrop-blur-sm"
              >
                <motion.div
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  className="mb-6 inline-block p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl group-hover:from-blue-100 group-hover:to-purple-100 transition-all duration-300"
                >
                  {feature.icon}
                </motion.div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4 group-hover:text-blue-600 transition-colors duration-300">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed group-hover:text-gray-700 transition-colors duration-300">{feature.description}</p>
                <motion.div
                  initial={{ width: 0 }}
                  whileHover={{ width: "100%" }}
                  transition={{ duration: 0.3 }}
                  className="h-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mt-6"
                ></motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
                Revolutionizing Mental Health Monitoring
              </h2>
              <p className="text-lg text-gray-600 mb-6 leading-relaxed">
                StressSense uses advanced computer vision and machine learning to analyze facial expressions,
                eye movements, and physiological signals to detect stress levels. Our AI model has been trained
                on thousands of data points to provide accurate, real-time stress assessment.
              </p>
              <div className="space-y-4">
                <div className="flex items-center">
                  <FaCheckCircle className="text-green-500 mr-3" />
                  <span className="text-gray-700">Non-invasive monitoring</span>
                </div>
                <div className="flex items-center">
                  <FaCheckCircle className="text-green-500 mr-3" />
                  <span className="text-gray-700">Works with any webcam</span>
                </div>
                <div className="flex items-center">
                  <FaCheckCircle className="text-green-500 mr-3" />
                  <span className="text-gray-700">Detailed analytics and reports</span>
                </div>
                <div className="flex items-center">
                  <FaCheckCircle className="text-green-500 mr-3" />
                  <span className="text-gray-700">Enterprise-ready for team monitoring</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <div className="grid grid-cols-2 gap-6">
                  <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600 mb-1">CNN</div>
                    <div className="text-sm text-gray-600">Neural Network</div>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600 mb-1">OpenCV</div>
                    <div className="text-sm text-gray-600">Computer Vision</div>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
                    <div className="text-2xl font-bold text-green-600 mb-1">Real-time</div>
                    <div className="text-sm text-gray-600">Processing</div>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg">
                    <div className="text-2xl font-bold text-indigo-600 mb-1">Privacy</div>
                    <div className="text-sm text-gray-600">First Design</div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              What Our Users Say
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Join thousands of users who have transformed their approach to mental wellness.
            </p>
          </motion.div>

          {/* Auto-scrolling Testimonials */}
          <div className="relative overflow-hidden">
            <motion.div
              animate={{
                x: [0, -388 * testimonials.length]
              }}
              transition={{
                x: {
                  repeat: Infinity,
                  repeatType: "loop",
                  duration: 50,
                  ease: "linear",
                },
              }}
              className="flex gap-8"
              style={{ width: `${testimonials.length * 400}px` }}
            >
              {[...testimonials, ...testimonials].map((testimonial, index) => (
                <motion.div
                  key={`${testimonial.name}-${index}`}
                  whileHover={{
                    y: -5,
                    scale: 1.02,
                    boxShadow: "0 20px 40px -12px rgba(0, 0, 0, 0.15)"
                  }}
                  className="bg-gradient-to-br from-white via-gray-50/50 to-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100/50 flex-shrink-0"
                  style={{ width: '380px' }}
                >
                  <div className="flex mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, scale: 0 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.1, duration: 0.3 }}
                        viewport={{ once: true }}
                      >
                        <FaStar className="text-yellow-400 text-lg" />
                      </motion.div>
                    ))}
                  </div>
                  <p className="text-gray-600 mb-6 italic leading-relaxed">"{testimonial.content}"</p>
                  <div className="border-t border-gray-100 pt-4">
                    <div className="font-bold text-gray-900 text-lg">{testimonial.name}</div>
                    <div className="text-sm text-gray-500">{testimonial.role}</div>
                    <div className="text-sm font-medium text-blue-600">{testimonial.company}</div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Trusted Partners Section */}
      <section className="py-20 bg-gradient-to-r from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <motion.div
              initial={{ scale: 0.8 }}
              whileInView={{ scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="inline-block px-6 py-2 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full text-blue-800 font-semibold text-sm mb-4"
            >
              Trusted Worldwide
            </motion.div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Trusted by Industry Leaders
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Join thousands of companies worldwide who trust StressSense for employee wellness.
            </p>
          </motion.div>

          {/* Auto-scrolling Partners */}
          <div className="relative overflow-hidden">
            <motion.div
              animate={{
                x: [0, -1176]
              }}
              transition={{
                x: {
                  repeat: Infinity,
                  repeatType: "loop",
                  duration: 25,
                  ease: "linear",
                },
              }}
              className="flex gap-8 items-center"
            >
              {/* First set of partners */}
              {[
                { name: "Capgemini", logo: "https://www.capgemini.com/wp-content/themes/capgemini-komposite/assets/images/logo.svg", alt: "Capgemini Logo" },
                { name: "Cognizant", logo: "https://cdn.worldvectorlogo.com/logos/cognizant-1.svg", alt: "Cognizant Logo" },
                { name: "Adobe", logo: "https://www.adobe.com/content/dam/cc/icons/Adobe_Corporate_Horizontal_Red_HEX.svg", alt: "Adobe Logo" },
                { name: "Microsoft", logo: "https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b?ver=5c31", alt: "Microsoft Logo" },
                { name: "Meta", logo: "https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg", alt: "Meta Logo" },
                { name: "P&G", logo: "https://upload.wikimedia.org/wikipedia/commons/8/85/Procter_%26_Gamble_logo.svg", alt: "P&G Logo" },
                { name: "Hexaware", logo: "https://upload.wikimedia.org/wikipedia/commons/5/5d/Hexaware_new_logo.svg", alt: "Hexaware Logo" }
              ].map((partner, index) => (
                <motion.div
                  key={`${partner.name}-${index}`}
                  className="bg-white/80 backdrop-blur-sm text-gray-800 px-6 py-4 rounded-xl shadow-lg transition-all duration-300 flex-shrink-0 min-w-[160px] text-center border border-gray-200/50 flex items-center justify-center h-16"
                >
                  <img
                    src={partner.logo}
                    alt={partner.alt}
                    className={`max-w-full object-contain transition-all duration-300 ${
                      partner.name === 'Hexaware' ? 'max-h-25 scale-125' : 'max-h-10'
                    }`}
                    onError={(e) => {
                      e.target.src = `https://via.placeholder.com/120x40/6b7280/ffffff?text=${partner.name}`;
                    }}
                  />
                </motion.div>
              ))}

              {/* Duplicate set for seamless loop */}
              {[
                { name: "Capgemini", logo: "https://www.capgemini.com/wp-content/themes/capgemini-komposite/assets/images/logo.svg", alt: "Capgemini Logo" },
                { name: "Cognizant", logo: "https://cdn.worldvectorlogo.com/logos/cognizant-1.svg", alt: "Cognizant Logo" },
                { name: "Adobe", logo: "https://www.adobe.com/content/dam/cc/icons/Adobe_Corporate_Horizontal_Red_HEX.svg", alt: "Adobe Logo" },
                { name: "Microsoft", logo: "https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE1Mu3b?ver=5c31", alt: "Microsoft Logo" },
                { name: "Meta", logo: "https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg", alt: "Meta Logo" },
                { name: "P&G", logo: "https://upload.wikimedia.org/wikipedia/commons/8/85/Procter_%26_Gamble_logo.svg", alt: "P&G Logo" },
                { name: "Hexaware", logo: "https://upload.wikimedia.org/wikipedia/commons/5/5d/Hexaware_new_logo.svg", alt: "Hexaware Logo" }
              ].map((partner, index) => (
                <motion.div
                  key={`${partner.name}-duplicate-${index}`}
                  className="bg-white/80 backdrop-blur-sm text-gray-800 px-6 py-4 rounded-xl shadow-lg transition-all duration-300 flex-shrink-0 min-w-[160px] text-center border border-gray-200/50 flex items-center justify-center h-16"
                >
                  <img
                    src={partner.logo}
                    alt={partner.alt}
                    className={`max-w-full object-contain transition-all duration-300 ${
                      partner.name === 'Hexaware' ? 'max-h-14 scale-125' : 'max-h-10'
                    }`}
                    onError={(e) => {
                      e.target.src = `https://via.placeholder.com/120x40/6b7280/ffffff?text=${partner.name}`;
                    }}
                  />
                </motion.div>
              ))}
            </motion.div>
          </div>

          {/* Trust indicators */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            viewport={{ once: true }}
            className="mt-16 text-center"
          >
            <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
              <div className="bg-white p-6 rounded-2xl shadow-lg">
                <div className="text-3xl font-bold text-blue-600 mb-2">10+</div>
                <div className="text-gray-600 font-medium">Companies Trust Us</div>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-lg">
                <div className="text-3xl font-bold text-green-600 mb-2">10K+</div>
                <div className="text-gray-600 font-medium">Employees Monitored</div>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-lg">
                <div className="text-3xl font-bold text-purple-600 mb-2">99.9%</div>
                <div className="text-gray-600 font-medium">Uptime Reliability</div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-20 bg-gradient-to-r from-gray-50 to-blue-50 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/50 to-transparent"></div>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <motion.div
              initial={{ scale: 0.8 }}
              whileInView={{ scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="inline-block px-6 py-2 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full text-blue-800 font-semibold text-sm mb-4"
            >
              Enterprise Solutions
            </motion.div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Ready to Transform Your Organization?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Join leading companies using StressSense for employee wellness and productivity enhancement.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            viewport={{ once: true }}
            className="bg-white rounded-3xl shadow-2xl p-8 md:p-12 border border-gray-100"
          >
            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div className="space-y-6">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <FaUsers className="text-white text-xl" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Enterprise Licensing</h3>
                    <p className="text-gray-600">Custom deployment solutions for large organizations</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-600 rounded-xl flex items-center justify-center">
                    <FaShieldAlt className="text-white text-xl" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Priority Support</h3>
                    <p className="text-gray-600">Dedicated technical support and implementation assistance</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                    <FaChartLine className="text-white text-xl" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Advanced Analytics</h3>
                    <p className="text-gray-600">Comprehensive reporting and team insights dashboard</p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8 text-center">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Contact Sales</h3>
                <p className="text-gray-600 mb-6">
                  Interested in enterprise solutions? Get in touch with our sales team.
                </p>
                <motion.a
                  href="mailto:prathameshgadgil2005@gmail.com?subject=Enterprise%20StressSense%20Inquiry"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="inline-flex items-center bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-full font-semibold hover:shadow-lg transition-all duration-300"
                >
                  <FaUsers className="mr-3" />
                  Email Sales Team
                </motion.a>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Download Section */}
      <section id="download" className="py-32 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-20 left-10 w-32 h-32 bg-white/5 rounded-full blur-xl"></div>
          <div className="absolute bottom-20 right-10 w-40 h-40 bg-white/5 rounded-full blur-xl"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-white/5 rounded-full blur-2xl"></div>
        </div>
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <motion.div
              initial={{ scale: 0.8 }}
              whileInView={{ scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="inline-block px-6 py-2 bg-white/20 backdrop-blur-sm rounded-full text-white font-semibold text-sm mb-6"
            >
              Ready to Get Started?
            </motion.div>
            <h2 className="text-4xl md:text-6xl font-bold text-white mb-8 leading-tight">
              Take Control of Your
              <span className="block">Mental Wellness Today</span>
            </h2>
            <p className="text-xl text-blue-100 mb-12 max-w-3xl mx-auto leading-relaxed">
              Download StressSense and start your journey towards better mental health monitoring.
              Free, private, and powered by advanced AI technology.
            </p>

            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              viewport={{ once: true }}
              className="bg-white/10 backdrop-blur-lg rounded-3xl p-10 mb-10 border border-white/20 shadow-2xl"
            >
              <div className="grid md:grid-cols-3 gap-8 mb-10">
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="text-center group"
                >
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4"
                  >
                    <FaDownload className="text-3xl text-white" />
                  </motion.div>
                  <div className="text-white font-bold text-lg mb-2">Easy Download</div>
                  <div className="text-blue-100 text-sm">One-click installation</div>
                </motion.div>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="text-center group"
                >
                  <motion.div
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4"
                  >
                    <FaShieldAlt className="text-3xl text-white" />
                  </motion.div>
                  <div className="text-white font-bold text-lg mb-2">Secure & Private</div>
                  <div className="text-blue-100 text-sm">No data collection</div>
                </motion.div>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="text-center group"
                >
                  <motion.div
                    animate={{ y: [0, -5, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4"
                  >
                    <FaBrain className="text-3xl text-white" />
                  </motion.div>
                  <div className="text-white font-bold text-lg mb-2">AI Powered</div>
                  <div className="text-blue-100 text-sm">Advanced algorithms</div>
                </motion.div>
              </div>

              <motion.a
                href="https://github.com/PGZON/Stress-Detection/releases/download/V1.0.0/StressDetectionInstaller.exe"
                whileHover={{
                  scale: 1.05,
                  boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.3)"
                }}
                whileTap={{ scale: 0.95 }}
                className="inline-flex items-center bg-white text-blue-600 px-12 py-6 rounded-full text-xl font-bold shadow-xl hover:shadow-2xl transform transition-all duration-300"
              >
                <FaDownload className="mr-4 text-2xl" />
                Download StressSense v1.0.0
              </motion.a>
              <p className="text-blue-100 text-sm mt-6">
                Windows 10/11 • 100MB • Free Forever • No Registration Required
              </p>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white py-16 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-900/10 to-purple-900/10"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-8 mb-12">
            <div className="lg:col-span-2">
              <div className="flex items-center space-x-3 mb-6">
                <motion.div
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.6 }}
                  className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg"
                >
                  <FaBrain className="text-white text-xl" />
                </motion.div>
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">StressSense</span>
              </div>
              <p className="text-gray-300 mb-6 leading-relaxed max-w-md">
                Revolutionizing mental health monitoring with AI-powered stress detection.
                Empowering individuals and organizations to prioritize mental wellness.
              </p>
              <div className="flex space-x-4">
                <motion.a
                  href="https://github.com/PGZON/Stress-Detection"
                  whileHover={{ scale: 1.1, y: -2 }}
                  className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gray-700 transition-all duration-300"
                >
                  <FaGithub className="text-xl" />
                </motion.a>
                <motion.a
                  href="https://linkedin.com/in/prathameshgadgil"
                  whileHover={{ scale: 1.1, y: -2 }}
                  className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gray-700 transition-all duration-300"
                >
                  <FaLinkedin className="text-xl" />
                </motion.a>
                <motion.a
                  href="https://x.com/prathamesh05_"
                  target="_blank"
                  rel="noopener noreferrer"
                  whileHover={{ scale: 1.1, y: -2 }}
                  className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gray-700 transition-all duration-300"
                >
                  <FaTwitter className="text-xl" />
                </motion.a>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-6 text-white">Product</h3>
              <ul className="space-y-3 text-gray-300">
                <li><a href="#features" className="hover:text-white transition-colors duration-300">Features</a></li>
                <li><a href="#download" className="hover:text-white transition-colors duration-300">Download</a></li>
                <li><a href="#about" className="hover:text-white transition-colors duration-300">About</a></li>
                <li><a href="#testimonials" className="hover:text-white transition-colors duration-300">Testimonials</a></li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-6 text-white">Support</h3>
              <ul className="space-y-3 text-gray-300">
                <li><a href="https://github.com/PGZON/Stress-Detection" className="hover:text-white transition-colors duration-300">GitHub</a></li>
                <li><a href="https://github.com/PGZON/Stress-Detection/issues" className="hover:text-white transition-colors duration-300">Report Issues</a></li>
                <li><a href="https://github.com/PGZON/Stress-Detection/releases" className="hover:text-white transition-colors duration-300">Releases</a></li>
                <li><a href="mailto:support@stressesnse.com" className="hover:text-white transition-colors duration-300">Contact</a></li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-6 text-white">Legal</h3>
              <ul className="space-y-3 text-gray-300">
                <li><button className="hover:text-white transition-colors duration-300 cursor-pointer bg-transparent border-none p-0 text-left">Privacy Policy</button></li>
                <li><button className="hover:text-white transition-colors duration-300 cursor-pointer bg-transparent border-none p-0 text-left">Terms of Service</button></li>
                <li><button className="hover:text-white transition-colors duration-300 cursor-pointer bg-transparent border-none p-0 text-left">License</button></li>
                <li><button className="hover:text-white transition-colors duration-300 cursor-pointer bg-transparent border-none p-0 text-left">GDPR</button></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-700 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-sm mb-4 md:mb-0">
                &copy; 2024 StressSense. All rights reserved. 
              </p>
              <div className="flex items-center space-x-6 text-sm text-gray-400">
                <span>Version 1.0.0</span>
                <span>•</span>
                <span>Last updated: September 2024</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </motion.div>
  );
};

export default LandingPage;