using System;
using Newtonsoft.Json;

namespace PostHog.Model
{
    public class BaseAction
    {
        public BaseAction(string @event, string? distinctId, Properties? properties = null, DateTime? timestamp = null)
        {
            Event = @event;
            DistinctId = distinctId;
            Properties = properties;
            Timestamp = timestamp ?? DateTime.UtcNow;
        }

        [JsonIgnore]
        public string? DistinctId { get; set; }

        [JsonProperty(PropertyName = "event")]
        public string Event { get; set; }

        [JsonProperty(PropertyName = "properties")]
        public Properties? Properties { get; set; }

        public int Size { get; set; }

        [JsonProperty(PropertyName = "timestamp")]
        public DateTime Timestamp { get; set; }
    }
}
