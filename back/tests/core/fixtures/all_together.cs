using System;
// New line yo !
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

        public string? DistinctId { get; set; }

        [JsonProperty(PropertyName = "event")]
        public string Event { get; set; }

        [JsonProperty(PropertyName = "properties")]
        public Properties? Properties { get; set; }

        [JsonDataIgnore]
        public int ChangedSize { get; set; }

        [JsonProperty(PropertyName = "timestamp")]
        public DateTime Timestamp { get; set; }
    }
}
