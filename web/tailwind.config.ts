import type { Config } from "tailwindcss";
const config: Config = { darkMode: ["class"], content: ["./app/**/*.{ts,tsx}","./components/**/*.{ts,tsx}"], theme: {
  extend: { colors: { cream:"#FEEECC","peach-sand":"#F0CFA8",maize:"#D4A986","tamarind-orange":"#F19738","chili-red":"#D7430C","clay-umber":"#B77850","burnt-sienna":"#8A4D31","cacao-brown":"#57180F"},
            borderRadius:{xl:"0.75rem","2xl":"1rem"}, boxShadow:{soft:"0 8px 24px rgba(0,0,0,0.06)"} } }, plugins: [] }; export default config;