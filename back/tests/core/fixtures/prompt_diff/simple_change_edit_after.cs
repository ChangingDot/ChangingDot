1using System;
2using Newtonsoft.Json;
3
4namespace PostHog.Model
5{
6    public class BaseAction
7    {
8        public BaseAction(string @event, string? distinctId, Properties? properties = null, DateTime? timestamp = null)
9        {
            // ERROR Error text
10            Event = @event;
11            DistinctId = distinctId;
12            Properties = properties;
13            Timestamp = timestamp ?? DateTime.UtcNow;
14        }
15
16-        [JsonIgnore]
+        [DifferentJsonIgnore]
17        public string? DistinctId { get; set; }
18
19        [JsonProperty(PropertyName = "event")]
20        public string Event { get; set; }
21
22        [JsonProperty(PropertyName = "properties")]
23        public Properties? Properties { get; set; }
24
25        [JsonIgnore]
26        public int Size { get; set; }
27
28        [JsonProperty(PropertyName = "timestamp")]
29        public DateTime Timestamp { get; set; }
30    }
31}