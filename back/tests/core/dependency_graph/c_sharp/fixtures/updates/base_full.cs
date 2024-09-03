using System;

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
        public int Size { get; set; }
    }
}